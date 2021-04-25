import numpy as np
from scipy.spatial.transform import Rotation as R
from magpylib._lib.utility import format_obj_input, get_good_path_length, all_same
from magpylib._lib.fields.field_wrap_BH_level1 import getBH_level1
from magpylib._lib.exceptions import MagpylibBadUserInput
from magpylib import _lib


def scr_dict_dipole(group: list, poso: np.ndarray) -> dict:
    """ Helper funtion that generates getBH_level1 input dict for Dipoles.

    Parameters
    ----------
    - group: list of sources
    - posov: ndarray, shape (m,sum(ni),3), pos_obs flattened

    Returns
    -------
    dict for getBH_level1 input
    """
    # pylint: disable=protected-access

    # generate indices
    l_group = len(group)    # no. sources in group
    m = len(group[0]._pos)  # path length
    mn = len(poso)          # path length * no. pixel
    n = int(mn/m)           # no. pixel

    # allocate dict arrays, shape: (l_group, m, n)
    momv = np.empty((l_group*mn,3))         # source mag
    posv = np.empty((l_group*mn,3))         # source pos
    rotv = np.empty((l_group*mn,4))         # source rot
    posov = np.tile(poso, (l_group,1))

    # fill dict arrays
    for i,src in enumerate(group):
        momv[i*mn:(i+1)*mn] = np.tile(src.moment, (mn,1))
        posv[i*mn:(i+1)*mn] = np.tile(src._pos,n).reshape(mn,3)
        rotv[i*mn:(i+1)*mn] = np.tile(src._rot.as_quat(),n).reshape(mn,4)
    # genreate rot object from rot input
    rotobj = R.from_quat(rotv)
    # generate dict and return
    src_dict = {'moment':momv, 'pos':posv, 'pos_obs': posov, 'rot':rotobj}
    return src_dict


def scr_dict_homo_mag(group: list, poso: np.ndarray) -> dict:
    """ Helper funtion that generates getBH_level1 input dict for homogeneous magnets.

    Parameters
    ----------
    - group: list of sources
    - posov: ndarray, shape (m,sum(ni),3), pos_obs flattened

    Returns
    -------
    dict for getBH_level1 input
    """
    # pylint: disable=protected-access

    # Sphere input requires slightly different index arrangement
    flag_sphere = isinstance(group[0],_lib.obj_classes.Sphere)

    # generate indices
    l_group = len(group)    # no. sources in group
    m = len(group[0]._pos)  # path length
    mn = len(poso)          # path length * no. pixel
    n = int(mn/m)           # no. pixel
    if flag_sphere:
        len_dim = 1                         # Sphere dim=scalar
    else:
        len_dim = len(group[0].dim)         # source type dim shape

    # allocate dict arrays, shape: (l_group, m, n)
    magv = np.empty((l_group*mn,3))         # source mag
    dimv = np.empty((l_group*mn,len_dim))   # source dim
    posv = np.empty((l_group*mn,3))         # source pos
    rotv = np.empty((l_group*mn,4))         # source rot
    posov = np.tile(poso, (l_group,1))

    # fill dict arrays
    for i,src in enumerate(group):
        magv[i*mn:(i+1)*mn] = np.tile(src.mag, (mn,1))
        dimv[i*mn:(i+1)*mn] = np.tile(src.dim, (mn,1))
        posv[i*mn:(i+1)*mn] = np.tile(src._pos,n).reshape(mn,3)
        rotv[i*mn:(i+1)*mn] = np.tile(src._rot.as_quat(),n).reshape(mn,4)
    # genreate rot object from rot input
    rotobj = R.from_quat(rotv)
    # make Sphere dim a 1D ndarray [x,x,x,x,x] or [x]
    if flag_sphere:
        dimv = dimv.T[0]
    # generate dict and return
    src_dict = {'mag':magv, 'dim':dimv, 'pos':posv, 'pos_obs': posov, 'rot':rotobj}
    return src_dict


def getBH_level2(bh, sources, observers, sumup, squeeze) -> np.ndarray:
    """...

    Parameters
    ----------
    - bh (bool): True=getB, False=getH
    - sources (src_obj or list): source object or 1D list of L sources/collections with similar
        pathlength M and/or 1.
    - observers (sens_obj or list or pos_obs): pos_obs or sensor object or 1D list of K sensors with
        similar pathlength M and/or 1 and sensor pos_pix of shape (N1,N2,...,3).
    - sumup (bool): default=False returns [B1,B2,...] for every source, True returns sum(Bi)
        for all sources.
    - squeeze (bool): default=True, If True output is squeezed (axes of length 1 are eliminated)

    Returns
    -------
    field: ndarray, shape squeeze((L,M,K,N1,N2,...,3)), field of L sources, M path
    positions, K sensors and N1xN2x.. observer positions and 3 field components.

    Info:
    -----
    - generates a 1D list of sources (collections flattened) and a 1D list of sensors from input
    - tile all paths of static (path_length=1) objects
    - combine all sensor pixel positions for joint evaluation
    - group similar source types for joint evaluation
    - compute field and store in allocated array
    - rearrange the array in the shape squeeze((L, M, K, N1, N2, ...,3))
    """
    # pylint: disable=protected-access
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    # avoid circular imports --------------------------------------------------
    Box = _lib.obj_classes.Box
    Cylinder = _lib.obj_classes.Cylinder
    Sphere = _lib.obj_classes.Sphere
    Collection = _lib.obj_classes.Collection
    Sensor = _lib.obj_classes.Sensor
    Dipole = _lib.obj_classes.Dipole

    # format input -------------------------------------------------------------
    if not isinstance(sources, list):          # input = a single source (or collection)
        sources = [sources]
    src_list = format_obj_input(sources) # flatten Collections

    if isinstance(observers, Sensor):                 # input = Sensor
        sensors = [observers]
    elif isinstance(observers, (tuple,np.ndarray)):   # input = tuple or ndarray
        sensors = [Sensor(pos_pix=observers)]
    elif isinstance(observers, list):                 # input = list
        if any(isinstance(obs,Sensor) for obs in observers):   # input = [sensor, tuple, senor, ...]
            sensors = []
            for obs in observers:
                if isinstance(obs, Sensor):
                    sensors += [obs]
                else:
                    sensors += [Sensor(pos_pix=obs)]
        else:                                  # input = [(1,2,3), (1,2,3), ...]
            sensors = [Sensor(pos_pix=observers)]

    # perform sensor checks ----------------------------------------------------

    # check if all observer input shapes are similar. Cannot accept different input shapes as
    #   it would lead to incomplete axes in the return arrays.
    pix_shapes = [sens.pos_pix.shape for sens in sensors]
    if not all_same(pix_shapes):
        raise MagpylibBadUserInput('Different observer input shapes not allowed.'+
            ' All pos_pix and pos_obs input shapes must be similar !')
    pix_shape = pix_shapes[0]

    # determine which sensors have unit roation so that they dont have to be rotated back later
    #   this check is made now when sensor paths are not yet tiled.
    unitQ = np.array([0,0,0,1.])
    unrotated_sensors = [all(all(r==unitQ) for r in sens._rot.as_quat()) for sens in sensors]

    # detemine which sensors have a static orientation (static sensor or translation path)
    static_sensor_rot = []
    for sens in sensors:
        if len(sens._pos)==1:           # no sensor path (sensor is static)
            static_sensor_rot += [True]
        else:                           # there is a sensor path
            rot = sens.rot.as_quat()
            if np.all(rot == rot[0]):          # path with static orient
                static_sensor_rot += [True]
            else:                              # sensor rotation changes along path
                static_sensor_rot += [False]

    # some important quantities -------------------------------------------------
    obj_list = src_list + sensors
    l0 = len(sources)
    l = len(src_list)
    k = len(sensors)

    # input path check + tile up static objects --------------------------------
    # tile up length 1 paths
    #    error if any path format is bad
    #    error if any path length is not m or 1
    m = get_good_path_length(obj_list)
    # store pointers to objects that are tiled up
    reset_objects = []
    if m>1:
        for obj in obj_list: # can have same obj several times in obj_list through a collection
            if len(obj._pos) == 1:
                reset_objects += [obj]
                obj.pos = np.tile(obj.pos, (m,1))
                rotq = np.tile(obj._rot.as_quat(), (m,1))
                obj.rot = R.from_quat(rotq)

    # combine information form all sensors to generate pos_obs with-------------
    #   shape (m * concat all sens flat pos_pix, 3)
    #   allows sensors with different pos_pix shapes
    poso =[[r.apply(sens.pos_pix.reshape(-1,3)) + p
            for r,p in zip(sens._rot, sens._pos)]
           for sens in sensors] # shape (k, nk, 3)
    poso = np.concatenate(poso,axis=1).reshape(-1,3)
    mn = len(poso)
    n = int(mn/m)

    # group similar source types----------------------------------------------
    src_sorted = [[],[],[],[]]   # store groups here
    order = [[],[],[],[]]        # keep track of the source order
    for i,src in enumerate(src_list):
        if isinstance(src, Box):
            src_sorted[0] += [src]
            order[0] += [i]
        elif isinstance(src, Cylinder):
            src_sorted[1] += [src]
            order[1] += [i]
        elif isinstance(src, Sphere):
            src_sorted[2] += [src]
            order[2] += [i]
        elif isinstance(src, Dipole):
            src_sorted[3] += [src]
            order[3] += [i]
        else:
            raise MagpylibBadUserInput('Unrecognized object in sources input')

    # evaluate each non-empty group in one go -------------------------------
    B = np.empty((l,m,n,3)) # store B-values here

    # Box group
    iii = 0
    group = src_sorted[iii]
    if group:
        lg = len(group)
        src_dict = scr_dict_homo_mag(group, poso)             # compute array dict for level1
        B_group = getBH_level1(bh=bh, src_type='Box', **src_dict) # compute field
        B_group = B_group.reshape((lg,m,n,3))         # reshape
        for i in range(lg):                           # put at dedicated positions in B
            B[order[iii][i]] = B_group[i]

    # Cylinder group
    iii = 1
    group = src_sorted[iii]
    if group:
        lg = len(group)
        src_dict = scr_dict_homo_mag(group, poso)
        B_group = getBH_level1(bh=bh, src_type='Cylinder', **src_dict)
        B_group = B_group.reshape((lg,m,n,3))
        for i in range(lg):
            B[order[iii][i]] = B_group[i]

    # Sphere group
    iii = 2
    group = src_sorted[iii]
    if group:
        lg = len(group)
        src_dict = scr_dict_homo_mag(group, poso)             # compute array dict for level1
        B_group = getBH_level1(bh=bh, src_type='Sphere', **src_dict) # compute field
        B_group = B_group.reshape((lg,m,n,3))         # reshape
        for i in range(lg):                           # put at dedicated positions in B
            B[order[iii][i]] = B_group[i]

    # Dipole group
    iii = 3
    group = src_sorted[iii]
    if group:
        lg = len(group)
        src_dict = scr_dict_dipole(group, poso)             # compute array dict for level1
        B_group = getBH_level1(bh=bh, src_type='Dipole', **src_dict) # compute field
        B_group = B_group.reshape((lg,m,n,3))         # reshape
        for i in range(lg):                           # put at dedicated positions in B
            B[order[iii][i]] = B_group[i]

    # reshape output ----------------------------------------------------------------
    # rearrange B when there is at least one Collection with more than one source
    if l > l0:
        for i,src in enumerate(sources):
            if isinstance(src, Collection):
                col_len = len(src.sources)
                B[i] = np.sum(B[i:i+col_len],axis=0)    # set B[i] to sum of slice
                B = np.delete(B,np.s_[i+1:i+col_len],0) # delete remaining part of slice

    # apply sensor rotations (after summation over collections to reduce rot.apply operations)
    #   note: replace by math.prod with python 3.8 or later
    k_pixel = int(np.product(pix_shape[:-1])) # total number of pixel positions
    for i,sens in enumerate(sensors):         # cylcle through all sensors
        if not unrotated_sensors[i]:          # apply operations only to rotated sensors
            if static_sensor_rot[i]:          # special case: same rotation along path
                # select part where rot is applied
                Bpart = B[:,:,i*k_pixel:(i+1)*k_pixel]
                # change shape from (l0,m,k_pixel,3) to (P,3) for rot package
                Bpart_flat = np.reshape(Bpart, (k_pixel*l0*m,3))
                # apply sensor rotation
                Bpart_flat_rot = sens._rot[0].inv().apply(Bpart_flat)
                # overwrite Bpart in B
                B[:,:,i*k_pixel:(i+1)*k_pixel] = np.reshape(Bpart_flat_rot, (l0,m,k_pixel,3))
            else:                         # general case: different rotations along path
                for j in range(m): # THIS LOOP IS EXTREMELY SLOW !!!! github issue #283
                    Bpart = B[:,j,i*k_pixel:(i+1)*k_pixel]           # select part
                    Bpart_flat = np.reshape(Bpart, (k_pixel*l0,3))   # flatten for rot package
                    Bpart_flat_rot = sens._rot[j].inv().apply(Bpart_flat)  # apply rotation
                    B[:,j,i*k_pixel:(i+1)*k_pixel] = np.reshape(Bpart_flat_rot, (l0,k_pixel,3)) # ov

    # rearrange sensor-pixel shape
    sens_px_shape = (k,) + pix_shape
    B = B.reshape((l0,m)+sens_px_shape)


    if sumup:
        B = np.sum(B, axis=0)

    # reduce all size-1 levels
    if squeeze:
        B = np.squeeze(B)

    # reset tiled objects
    for obj in reset_objects:
        obj.pos = obj.pos[0]
        obj.rot = obj.rot[0]

    return B

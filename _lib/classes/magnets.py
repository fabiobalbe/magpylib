#!/usr/bin/env python3
# -*- coding: utf-8 -*-



#%% IMPORTS
from numpy import float64,isnan,array
from magPyLib._lib.mathLibPrivate import angleAxisRotation
import sys
from magPyLib._lib.fields.PM_Cube import Bfield_Cube
from magPyLib._lib.fields.PM_Cylinder import Bfield_Cylinder
from magPyLib._lib.fields.PM_Sphere import Bfield_Sphere
from magPyLib._lib.classes.base import HomoMag



#%% THE CUBE CLASS

class Cube(HomoMag):
    """ 
    This class represents a homogeneously magnetized rectangular magnet. In 
    the canonical basis (position=[0,0,0], angle=0, axis=[0,0,1]) the magnet
    has the origin at its geometric center and the sides of the cube are parallel
    to the basis vectors. Scalar input is either integer or float. 
    Vector input format can be either list, tuple or array of any data type (float, int).
    
    
    Class Initialization (only kwargs):
    ---------------------
    dim : vec3 [mm]
    
    mag : vec3 [mT]
        Set magnetization vector of magnet in units of [mT].
        
    dim : vec3 [mm]
        Set the size of the cube. dim=[A,B,C] which corresponds to the three
        side lenghts of the cube in units of [mm].
        
    pos=[0,0,0] : vec3 [mm]
        Set position of the center of the magnet in units of [mm].
    
    angle=0 : scalar [deg]
        Set angle of orientation of magnet in units of [deg].
    
    axis=[0,0,1] : vec3 []
        Set axis of orientation of the magnet.
    
    Class Variables:
    ----------------
    
    magnetization : arr3 [mT]
        Magnetization vector of cube in units of [mT].
        
    dimension : arr3 [mm]
        Magnet dimension=[A,B,C] which correspond to the three side lenghts
        of the cube in units of [mm] in x-,y- and z-direction respectively
        in the canonical basis.
    
    position : arr3 [mm]
        Position of the center of the magnet in units of [mm].
    
    angle : float [deg]
        Angle of orientation of the magnet in units of [deg].
        
    axis : arr3 []
        Axis of orientation of the magnet.
    
    Class Methods:
    --------------
    setPosition(newPos) : takes vec3[mm] - returns None
        Set `newPos` as new source position.
    
    move(displacement) : takes vec3[mm] - return None
        Moves source by the `displacement` argument.
    
    setOrientation(angle,axis) : takes float[deg],vec3[] - returns None
        Set new source orientation (angle and axis) to argument values.
    
    rotate(angle,axis,CoR=[0,0,0]) : takes float[deg],vec3[],kwarg(vec3)[mm] - returns None
        Rotate the source by `angle` about an axis parallel to `axis` running
        through center of rotation `CoR`.
    
    getB(pos) : takes vec3[mm] - returns arr3[mT]
        Gives the magnetic field generated by the source in units of [mT]
        at the position `pos`.
    
    Examples:
    ---------
    >>> import magPyLib as magpy
    >>> from time import clock
    >>> pm = magpy.magnet.Cube(mag=[0,0,1000],dim=[1,1,1])
    >>> T0 = clock()
    >>> B = pm.getB([1,0,1])
    >>> T1 = clock()
    >>> print(B)
      [42.9223532 0.0 13.7461635]
    >>> print(T1-T0)
      0.00047622195062974195
    """    
    def __init__(self, mag=None, dim=None, pos=(0,0,0), angle=0, axis=(0,0,1)):

        
        #inherit class HomoMag
        HomoMag.__init__(self,pos,angle,axis,mag)
        
        #secure input type and check input format of dim
        self.dimension = array(dim, dtype=float64, copy=False)
        if any(isnan(self.dimension))  or  len(self.dimension)!= 3:
            sys.exit('Bad dim input for cube')
        
        
    def getB(self,pos):
        """
        This method returns the magnetic field vector generated by the source 
        at the argument position `pos` in units of [mT]
        
        Parameters:
        ----------
        pos : vec3 [mm]
            Position where magnetic field should be determined.
        
        Returns:    
        --------
        magnetic field vector : arr3 [mT]
            Magnetic field at the argument position `pos` generated by the
            source in units of [mT].
        """
        #secure input type and check input format
        p1 = array(pos, dtype=float64, copy=False)
        
        #relative position between mag and obs
        posRel = p1 - self.position
        
        #rotate this vector into the CS of the magnet (inverse rotation)
        p21newCm = angleAxisRotation(self.angle,-self.axis,posRel)
        
        #the field is well known in the magnet coordinates
        BCm = Bfield_Cube(self.magnetization,p21newCm,self.dimension)  # obtain magnetic field in Cm
        
        #rotate field vector back
        B = angleAxisRotation(self.angle,self.axis,BCm)
        
        return B
    



#%% THE CYLINDER CLASS

class Cylinder(HomoMag):
    """ 
    This class represents a homogeneously magnetized cylinder (circular bottom)
    magnet. The magnet is initialized in the canonical basis (position=[0,0,0],
    angle=0, axis=[0,0,1]) with the geometric center at the origin and the
    central symmetry axis pointing in z-direction so that the circular bottom
    lies in a plane parallel to the xy-plane. Scalar input is either integer
    or float. Vector input format can be either list, tuple or array of any
    data type (float, int).
        
    Class Initialization (only kwargs):
    ---------------------
    
    mag : vec3 [mT]
        Set magnetization vector of magnet in units of [mT].
        
    dim : vec2 [mm]
        Set the size of the cylinder. dim=[D,H] which are diameter and height
        of the cylinder in units of [mm] respectively.
        
    pos=[0,0,0] : vec3 [mm]
        Set position of the center of the magnet in units of [mm].
    
    angle=0 : scalar [deg]
        Set angle of orientation of magnet in units of [deg].
    
    axis=[0,0,1] : vec3 []
        Set axis of orientation of the magnet.
        
    iterDia=50 : int []
        Set number of iterations for calculation of B-field from non-axial 
        magnetization. Lower values will make the calculation faster but
        less precise.
        
    Class Variables:
    ----------------
    
    magnetization : arr3 [mT]
        Magnetization vector of magnet in units of [mT].
        
    dimension : arr2 [mm]
        Magnet dimension=[D,H] which correspond to diameter and height of the
        cylinder in units of [mm].
    
    position : arr3 [mm]
        Position of the center of the magnet in units of [mm].
    
    angle : float [deg]
        Angle of orientation of the magnet in units of [deg].
        
    axis : arr3 []
        Axis of orientation of the magnet.
    
    iterDia : int []
        Number of iterations for calculation of B-field from non-axial
        magnetization. Lower values will make the calculation faster but less
        precise.
        
    Class Methods:
    --------------
    setPosition(newPos) : takes vec3[mm] - returns None
        Set `newPos` as new source position.
    
    move(displacement) : takes vec3[mm] - return None
        Moves source by the `displacement` argument.
    
    setOrientation(angle,axis) : takes float[deg],vec3[] - returns None
        Set new source orientation (angle and axis) to argument values.
    
    rotate(angle,axis,CoR=[0,0,0]) : takes float[deg],vec3[],kwarg(vec3)[mm] - returns None
        Rotate the source by `angle` about an axis parallel to `axis` running
        through center of rotation `CoR`.
    
    getB(pos) : takes vec3[mm] - returns arr3[mT]
        Gives the magnetic field generated by the source in units of [mT]
        at the position `pos`.
        
    Examples:
    ---------
    >>> import magPyLib as magPy
    >>> pm = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
    >>> B = pm.getB([1,0,1])
    >>> print(B)
      [34.31662243  0.         10.16090915]
    """ 
    def __init__(self, mag=None, dim=None, pos=(0,0,0), angle=0, axis=(0,0,1), iterDia = 50):

        
        #inherit class homoMag
        #   - pos, Mrot, MrotInv, mag
        #   - moveBy, rotateBy
        HomoMag.__init__(self,pos,angle,axis,mag)
        
        #secure input type and check input format of dim
        self.dimension = array(dim, dtype=float64, copy=False) 
        if any(isnan(self.dimension))  or  len(self.dimension)!= 2:
            sys.exit('Bad dim input for cylinder')
        self.iterDia = iterDia
        if not type(self.iterDia) == int:
            sys.exit('Bad iterDia input for cylinder')
        
    def getB(self,pos):
        """
        This method returns the magnetic field vector generated by the source 
        at the argument position `pos` in units of [mT]
        
        Parameters:
        ----------
        pos : vec3 [mm]
            Position where magnetic field should be determined.
        
        Returns:    
        --------
        magnetic field vector : arr3 [mT]
            Magnetic field at the argument position `pos` generated by the
            source in units of [mT].
        """
        #secure input type and check input format
        p1 = array(pos, dtype=float64, copy=False)
        
        #relative position between mag and obs
        posRel = p1 - self.position
        
        #rotate this vector into the CS of the magnet (inverse rotation)
        p21newCm = angleAxisRotation(self.angle,-self.axis,posRel)
        
        #the field is well known in the magnet coordinates
        BCm = Bfield_Cylinder(self.magnetization,p21newCm,self.dimension,self.iterDia)  # obtain magnetic field in Cm
        
        #rotate field vector back
        B = angleAxisRotation(self.angle,self.axis,BCm)
        
        return B
    
    



#%% THE SPHERE CLASS

class Sphere(HomoMag):
    """ 
    This class represents a homogeneously magnetized sphere. The magnet
    is initialized in the canonical basis (position=[0,0,0],
    angle=0, axis=[0,0,1]) with the center at the origin. Scalar input is
    either integer or float. Vector input format can be either list, tuple
    or array of any data type (float, int).
    
    Class Initialization (only kwargs):
    ---------------------
    
    mag : vec3 [mT]
        Set magnetization vector of magnet in units of [mT].
        
    dim : float [mm]
        Set diameter of the sphere in units of [mm].
        
    pos=[0,0,0] : vec3 [mm]
        Set position of the center of the magnet in units of [mm].
    
    angle=0 : scalar [deg]
        Set angle of orientation of magnet in units of [deg].
    
    axis=[0,0,1] : vec3 []
        Set axis of orientation of the magnet.
    
    Class Variables:
    ----------------
    
    magnetization : arr3 [mT]
        Magnetization vector of magnet in units of [mT].
        
    dimension : float [mm]
        Sphere diameter in units of [mm].
    
    position : arr3 [mm]
        Position of the center of the magnet in units of [mm].
    
    angle : float [deg]
        Angle of orientation of the magnet in units of [deg].
        
    axis : arr3 []
        Axis of orientation of the magnet.
    
    Class Methods:
    --------------
    setPosition(newPos) : takes vec3[mm] - returns None
        Set `newPos` as new source position.
    
    move(displacement) : takes vec3[mm] - return None
        Moves source by the `displacement` argument.
    
    setOrientation(angle,axis) : takes float[deg],vec3[] - returns None
        Set new source orientation (angle and axis) to argument values.
    
    rotate(angle,axis,CoR=[0,0,0]) : takes float[deg],vec3[],kwarg(vec3)[mm] - returns None
        Rotate the source by `angle` about an axis parallel to `axis` running
        through center of rotation `CoR`.
    
    getB(pos) : takes vec3[mm] - returns arr3[mT]
        Gives the magnetic field generated by the source in units of [mT]
        at the position `pos`.
        
    Examples:
    ---------
    >>> import magPyLib as magPy
    >>> pm = magPy.magnet.Sphere(mag=[0,0,1000],dim=1)
    >>> B = pm.getB([1,0,1])
    >>> print(B)
      [22.09708691  0.          7.36569564]
    """ 
    def __init__(self, mag=None, dim=None, pos=(0,0,0), angle=0, axis=(0,0,1)):

        
        #inherit class homoMag
        #   - pos, Mrot, MrotInv, mag
        #   - moveBy, rotateBy
        HomoMag.__init__(self,pos,angle,axis,mag)
        
        #secure input type and check input format of dim
        self.dimension = float(dim)
        if self.dimension <= 0:
            sys.exit('Bad dim<0 for sphere')

    def getB(self,pos):
        """
        This method returns the magnetic field vector generated by the source 
        at the argument position `pos` in units of [mT]
        
        Parameters:
        ----------
        pos : vec3 [mm]
            Position where magnetic field should be determined.
        
        Returns:    
        --------
        magnetic field vector : arr3 [mT]
            Magnetic field at the argument position `pos` generated by the
            source in units of [mT].
        """
        #secure input type and check input format
        p1 = array(pos, dtype=float64, copy=False)
        
        #relative position between mag and obs
        posRel = p1 - self.position
        
        #rotate this vector into the CS of the magnet (inverse rotation)
        p21newCm = angleAxisRotation(self.angle,-self.axis,posRel)
        
        #the field is well known in the magnet coordinates
        BCm = Bfield_Sphere(self.magnetization,p21newCm,self.dimension)  # obtain magnetic field in Cm
        
        #rotate field vector back
        B = angleAxisRotation(self.angle,self.axis,BCm)
        
        return B
import numpy as np
import magpylib as magpy
from magpylib._src.fields.field_wrap_BH_level2_dict import getB_dict

def test_dipole_approximation():
    """ test if all source fields converge towards the correct dipole field at distance
    """
    mag = np.array([111,222,333])
    pos = (1234,-234, 345)

    # cuboid with volume = 1 mm^3
    src1 = magpy.magnet.Cuboid(mag, dimension=(1,1,1))
    B1 = src1.getB(pos)

    # Cylinder with volume = 1 mm^3
    dia = np.sqrt(4/np.pi)
    src2 = magpy.magnet.Cylinder(mag, dimension=(dia,1))
    B2 = src2.getB(pos)
    assert np.allclose(B1,B2)

    # Sphere with volume = 1 mm^3
    dia = (6/np.pi)**(1/3)
    src3 = magpy.magnet.Sphere(mag, dia)
    B3 = src3.getB(pos)
    assert np.allclose(B1,B3)

    #  Dipole with mom=mag
    src4 = magpy.misc.Dipole(moment=mag)
    B4 = src4.getB(pos)
    assert np.allclose(B1,B4)

    # Loop loop vs Dipole
    dia = 2
    i0 = 234
    m0 = dia**2 * np.pi**2 / 10 * i0
    src1 = magpy.current.Loop(current=i0, diameter=dia)
    src2 = magpy.misc.Dipole(moment=(0,0,m0))
    H1 = src1.getH(pos)
    H2 = src2.getH(pos)
    assert np.allclose(H1, H2)


def test_Loop_vs_Cylinder_field():
    """
    The H-field of a loop with radius r0[mm] and current i0[A] is the same
    as the H-field of a cylinder with radius r0[mm], height h0[mm] and
    magnetization (0, 0, 4pi/10*i0/h0) !!!
    """

    # this set of position generates a strange error in celv
    # that is now fixed. (some k2<0.04, some larger)
    pos_obs = np.array(
        [[2.62974227e-01, 8.47810369e-01, 1.08754479e+01],
         [3.84185491e-01, 2.95441595e-01, 1.00902470e+01],
         [6.42119527e-01, 2.06572582e-01, 1.00111349e+01],
         [2.77437481e-01, 7.70421483e-01, 1.01708024e+01],
         [6.38134375e-01, 6.60523111e-01, 1.02255165e+01],
         [4.05896210e-01, 7.18840810e-01, 1.09878512e+01],
         [4.25483323e-01, 5.97011185e-01, 1.03105633e+01],
         [1.86350557e-01, 9.45180347e-01, 1.00771425e+01],
         [7.31784172e-03, 3.43762111e-01, 1.01388689e+01],
         [9.76180294e-01, 2.86980987e-01, 1.07162604e+01],
         [4.19970335e-01, 6.78011898e-01, 1.07462700e+01],
         [2.51709117e-01, 1.80214678e-01, 1.05292310e+01],
         [1.38341488e-01, 7.64969048e-01, 1.04836868e+01],
         [7.16320259e-01, 5.17108288e-01, 1.04404834e+01],
         [1.36719186e-01, 8.03444934e-02, 1.05825844e+01],
         [3.02549448e-01, 8.01158793e-01, 1.06895803e+01],
         [6.96369978e-01, 8.41086725e-01, 1.05991355e+01],
         [1.56389836e-02, 8.83332094e-01, 1.00294123e+01],
         [5.72854015e-01, 9.78889329e-01, 1.00856741e+01],
         [5.90518725e-01, 2.71810008e-01, 1.09421650e+01],
         [9.78841160e-01, 8.49649719e-01, 1.02277205e+01],
         [3.34356881e-01, 4.85928671e-01, 1.08996289e+01],
         [4.57102605e-01, 7.29004951e-01, 1.06881211e+01],
         [7.70055121e-01, 7.79513350e-01, 1.00064163e+01],
         [4.38978477e-01, 2.42722989e-01, 1.07810591e+01],
         [2.94965451e-01, 8.16939582e-01, 1.08524609e+01],
         [9.10294019e-01, 1.01999675e-01, 1.05777031e+01],
         [1.98324922e-01, 8.69170938e-01, 1.06498450e+01],
         [2.04949091e-01, 7.29157637e-02, 1.08216263e+01],
         [4.03860840e-01, 2.51733457e-01, 1.09413861e+01],
         [8.42429689e-01, 7.53521494e-01, 1.06840432e+01],
         [5.47487506e-01, 2.17112793e-01, 1.08309858e+01],
         [1.32920817e-02, 8.90027375e-01, 1.05206045e+01],
         [2.12434323e-01, 1.07809620e-01, 1.05248679e+01],
         [9.24972525e-01, 4.02334232e-01, 1.01218881e+01],
         [4.72828420e-01, 8.84518608e-01, 1.03564702e+01],
         [7.47506193e-01, 8.50172276e-02, 1.08471793e+01],
         [5.59375134e-01, 7.49345280e-01, 1.04832901e+01],
         [1.53289823e-01, 1.22688627e-01, 1.01417979e+01],
         [6.20682956e-01, 2.04842717e-01, 1.02372747e+01],
         [5.26696817e-01, 9.97967209e-01, 1.01548900e+01],
         [3.12286750e-01, 8.55676144e-02, 1.08151431e+01],
         [3.36130598e-01, 9.23647162e-01, 1.01808101e+01],
         [6.48032234e-01, 6.77714891e-01, 1.06903143e+01],
         [4.97615700e-02, 6.86552664e-01, 1.04692230e+01],
         [1.39612563e-01, 5.94597678e-01, 1.09177616e+01],
         [9.49958586e-01, 3.03275707e-01, 1.04126750e+01],
         [7.90362802e-02, 2.05629309e-01, 1.08460663e+01],
         [6.39251869e-01, 1.27717311e-01, 1.03640598e+01],
         [1.75346719e-01, 7.76144247e-01, 1.07590716e+01],
         [4.80488839e-01, 6.44113412e-01, 1.00806087e+01],
         [3.30249230e-01, 2.90567396e-01, 1.02823508e+01],
         [2.32507704e-01, 3.11357670e-01, 1.00585207e+01],
         [9.93932043e-01, 8.13588626e-01, 1.02441850e+01],
         [6.14110393e-02, 8.24710989e-01, 1.03036766e+01],
         [7.54284742e-01, 4.75888115e-01, 1.02980990e+01],
         [9.03436653e-01, 1.38604212e-02, 1.02052852e+01],
         [3.25406232e-01, 5.01599309e-01, 1.02273729e+01],
         [6.10904352e-01, 2.01374297e-02, 1.05994945e+01],
         [5.13886308e-01, 7.47646233e-01, 1.00881973e+01],
         [7.66062767e-01, 8.55628912e-01, 1.02443255e+01],
         [4.12965850e-01, 6.71639134e-02, 1.08920383e+01],
         [2.22162237e-01, 4.35458370e-01, 1.00005670e+01],
         [6.92063517e-01, 4.77425107e-01, 1.09109479e+01],
         [4.73624739e-02, 5.67853047e-01, 1.02619257e+01],
         [7.35614319e-01, 3.04928294e-01, 1.04878104e+01],
         [9.52815588e-01, 1.83929502e-01, 1.09015172e+01],
         [6.85134024e-01, 2.56932032e-01, 1.06599932e+01],
         [7.49282874e-01, 6.99614619e-01, 1.04573794e+01],
         [8.06968804e-01, 8.99615103e-01, 1.06770292e+01],
         [8.10594977e-01, 9.37427828e-01, 1.04077535e+01],
         [3.52771587e-01, 4.62098593e-01, 1.02567372e+01],
         [5.65591895e-01, 2.76154469e-01, 1.05387184e+01],
         [2.46784605e-01, 5.66301118e-01, 1.00484832e+01],
         [4.54504276e-01, 3.50320293e-01, 1.09152037e+01],
         [1.34071712e-01, 3.18619591e-01, 1.09602583e+01],
         [7.06928981e-01, 1.30956872e-01, 1.01472973e+01],
         [9.24252364e-02, 3.09994386e-01, 1.04355552e+01],
         [4.70425188e-01, 7.59610285e-01, 1.03136298e+01],
         [7.04080112e-01, 4.16336685e-01, 1.03876008e+01],
         [8.44199888e-01, 4.84203700e-01, 1.06195388e+01],
         [6.75770202e-02, 6.31321589e-01, 1.06495791e+01],
         [9.48223738e-01, 8.77564164e-01, 1.09798880e+01],
         [1.21580775e-01, 8.75070086e-01, 1.08523342e+01],
         [4.15901288e-01, 7.58294704e-01, 1.09128418e+01],
         [3.42156748e-01, 5.05791032e-01, 1.07678098e+01],
         [4.64032116e-01, 7.28064777e-01, 1.09940092e+01],
         [7.72357996e-01, 7.78746013e-01, 1.07879828e+01],
         [2.02837991e-01, 5.09599429e-01, 1.04062704e+01],
         [1.88330581e-01, 3.84815757e-02, 1.01780565e+01],
         [2.57727724e-01, 1.27152743e-01, 1.09787027e+01],
         [2.11735849e-01, 3.98791360e-02, 1.00743078e+01],
         [6.59218472e-01, 3.79855821e-01, 1.09638287e+01],
         [3.64295183e-01, 1.31074260e-01, 1.08378312e+01],
         [8.79182622e-01, 4.45474832e-01, 1.09849294e+01],
         [7.26668838e-01, 9.74937759e-01, 1.05272224e+01],
         [4.05964529e-01, 1.45939524e-01, 1.09852591e+01],
         [2.10202133e-01, 9.20279331e-01, 1.06021266e+01],
         [7.05832473e-01, 9.51319508e-01, 1.09945602e+01],
         [7.78805359e-01, 6.72775055e-01, 1.03208115e+01],
         [5.44243955e-01, 5.63471403e-01, 1.09625371e+01],
         [8.45600648e-01, 9.05625429e-01, 1.06477723e+01],
         [9.34692923e-01, 9.70997998e-01, 1.05067462e+01],
         [9.57848052e-01, 4.33603497e-01, 1.04114712e+01],
         [8.09856480e-01, 5.51234361e-01, 1.07861471e+01],
         [3.52087564e-01, 4.35030132e-01, 1.02227394e+01],
         [4.26459999e-01, 4.04590274e-02, 1.00624838e+01],
         [6.40711056e-01, 7.64628524e-02, 1.06025149e+01],
         [4.50498913e-01, 6.60774849e-01, 1.03881413e+01],
         [3.61705605e-01, 1.01651959e-01, 1.08800255e+01],
         [4.07986797e-01, 9.62831662e-01, 1.09469213e+01]])

    r0 = 2
    h0 = 1e-4
    i0 = 1
    src1 = magpy.magnet.Cylinder(magnetization=(0,0,i0/h0*4*np.pi/10), dimension=(r0,h0))
    src2 = magpy.current.Loop(current=i0, diameter=r0)

    H1 = src1.getH(pos_obs)
    H2 = src2.getH(pos_obs)

    assert np.allclose(H1, H2)


def test_Line_vs_Loop():
    """ show that line prodices the same as circular
    """

   # finely approximated loop by lines
    ts = np.linspace(0,2*np.pi,10000)
    verts = np.array([(np.cos(t), np.sin(t), 0) for t in ts])
    ps = verts[:-1]
    pe = verts[1:]

    # positions
    ts = np.linspace(-3,3,2)
    po = np.array([(x,y,z) for x in ts for y in ts for z in ts])

    # field from line currents
    Bls = []
    for p in po:
        Bl = getB_dict(source_type='Line', observer=p, current=1,
            segment_start=ps, segment_end=pe)
        Bls += [np.sum(Bl, axis=0)]
    Bls = np.array(Bls)

    # field from current loop
    src = magpy.current.Loop(current=1, diameter=2)
    Bcs = src.getB(po)

    assert np.allclose(Bls,Bcs)


def test_Line_vs_Infinite():
    """ compare line current result vs analytical solution to infinite Line
    """

    pos_obs = np.array([(1.,2,3), (-3,2,-1), (2,-1,-4)])

    def Binf(i0, pos):
        """ field of inf line current on z-axis """
        x,y,_ = pos
        r = np.sqrt(x**2+y**2)
        e_phi = np.array([-y,x,0])
        e_phi = e_phi/np.linalg.norm(e_phi)
        mu0 = 4*np.pi*1e-7
        return i0*mu0/2/np.pi/r*e_phi * 1000 * 1000 #mT mm

    ps = (0,0,-1000000)
    pe = (0,0,1000000)
    Bls, Binfs = [], []
    for p in pos_obs:
        Bls += [getB_dict(source_type='Line', observer=p, current=1,
            segment_start=ps, segment_end=pe)]
        Binfs += [Binf(1,p)]
    Bls = np.array(Bls)
    Binfs = np.array(Binfs)

    assert np.allclose(Bls, Binfs)

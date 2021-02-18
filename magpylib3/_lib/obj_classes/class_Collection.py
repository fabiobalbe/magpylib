"""Collection class code"""

import copy
from magpylib3._lib.math_utility.utility import format_src_input, check_duplicates
from magpylib3._lib.fields.field_BHwrapper import getB, getH
from magpylib3._lib.graphics import display

class Collection:
    """ Group multiple sources in one Collection.
    
    ### Properties
    - sources (list): Ordered list of sources in the Collection

    ### Methods
    - move: move all sources simultaneously
    - rotate: rotate all sources (about the same anchor)
    - display: display the Collection graphically
    - getB: compute B-field of Collection
    - getH: compute H-field of Collection
    - add_sources: add sources to the Collection (no copy)
    - remove_source: remove a source from the Collection (no copy)

    ### Returns:
    - (Collection object)

    ### Info
    Collections have +/- operations defined to add and remove sources.
        (no copy is made)

    Collections are iterable, iterating through self.sources

    Collections have getitem defined, col[i] returns self.sources[i]
    """

    def __init__(self, *sources):

        self.sources = sources


    # sources properties --------------------------------------------
    @property
    def sources(self):
        """ list of sources in Collection
        """
        return self._sources


    @sources.setter
    def sources(self, sources):
        """ set sources in the Collection, arbitrary input
        """
        # format input
        src_list = format_src_input(sources)
        # check and eliminate duplicates
        src_list = check_duplicates(src_list)
        # set attributes
        self._sources = src_list


    # dunders -------------------------------------------------------
    def __add__(self, source):
        """ add sources or collections
        """
        self.add(source)
        return self
    

    def __sub__(self, source):
        """ remove a source from the Collection
        """
        self.remove(source)
        return self
    

    def __iter__(self):
        """ make Collection iterable
        """
        yield from self._sources
    

    def __getitem__(self,i):
        """ provide getitem property
        """
        return self._sources[i]


    # methods -------------------------------------------------------
    def add(self,*sources):
        """ Add arbitrary sources to Collection.

        ### Args:
        - sources (sequence of sources and collections): add arbitrary 
            sequences of sources and collections to the Collection.
            The new sources will be added at the end of self.sources.
            Duplicates will be eliminated.

        ### Returns:
        - self
        """

        # format input
        src_list = format_src_input(sources)
        # combine with original src_list
        src_list = self._sources + src_list
        # check and eliminate duplicates
        src_list = check_duplicates(src_list)
        # set attributes
        self._sources = src_list
        return self
    

    def remove(self,source):
        """ Remove source from collection

        ### Args:
        - source (source): remove source from Collection

        ### Returns:
        - self
        """
        self._sources.remove(source)
        return self
    

    def getB(self, pos_obs, **kwargs):
        """ Compute B-field of Collection at observer positions.

        ### Args:
        - pos_obs (N1 x N2 x ... x 3 vec): single position or set of 
            observer positions in units of mm.

        ### Returns:
        - (N1 x N2 x ... x 3 ndarray): B-field at observer positions
            in units of mT.
        """
        return getB(self, pos_obs, sumup=True, **kwargs)
    

    def getH(self, pos_obs, **kwargs):
        """ Compute H-field of Collection at observer positions.

        ### Args:
        - pos_obs (N1 x N2 x ... x 3 vec): single position or set of 
            observer positions in units of mm.

        ### Returns:
        - (N1 x N2 x ... x 3 ndarray): H-field at observer positions
            in units of kA/m.
        """
        return getH(self, pos_obs, sumup=True, **kwargs)


    def display(self, **kwargs):
        """ 
        Display Collection graphically. kwargs of top level display()
            function.
        """
        display(self, **kwargs)


    def move_by(self, displacement, steps=-1):
        """
        Linear displacement of Collection.

        Parameters
        ----------
        displacement: array_like, shape (3,)
            displacement vector in units of mm.
        
        steps: int, optional, default=-1
            If steps < 0: apply a linear motion from 0 to displ on top 
                of existing path[steps:]. Specifically, steps=-1 will just
                displace path[-1].
            If steps > 0: add linear displacement to existing path starting
                at path[-1].

        Returns:
        --------
        self : Collection
        """
        for s in self:
            s.move_by(displacement, steps)
        return self


    def rotate(self, rot, anchor=None, steps=-1):
        """ 
        Rotate all sources in Collection.

        Parameters
        ----------
        rot: scipy Rotation object
        
        anchor: None or array_like, shape (3,), default=None
            The axis of rotation passes through the anchor point. When anchor=None
            the object will rotate about its own center.

        steps: int, optional, default=-1
            If steps < 0: apply linear rotation steps from 0 to rot on top 
                of existing path[steps:]. Specifically, steps=-1 will just
                rotate path[-1].
            If steps > 0: add linear rotation steps from 0 to rot to existing
                path starting at path[-1].

        Returns:
        --------
        self : Collection
        """
        for s in self:
            s.rotate(rot, anchor, steps)
        return self


    def rotate_from_angax(self, angle, axis, anchor=None, steps=-1, degree=True):
        """ Rotate all sources in Collection.

        Parameters
        ----------
        angle: float
            Angle of rotation (in [deg] by default).
        
        axis: array_like, shape (3,)
            The axis of rotation [dimensionless]

        anchor: None or array_like, shape (3,), default=None
            The axis of rotation passes through the anchor point. By default 
            anchor=None the object will rotate about its own center.
        
        degree: bool, default=True
            If True, Angle is given in [deg]. If False, angle is given in [rad].
                    
        steps: int, optional, default=-1
            If steps < 0: apply linear rotation steps from 0 to rot on top 
                of existing path[steps:]. Specifically, steps=-1 will just
                rotate path[-1].
            If steps > 0: add linear rotation steps from 0 to rot to existing
                path starting at path[-1].

        Returns:
        --------
        self : Collection
        """
        for s in self:
            s.rotate_from_angax(angle, axis, anchor, steps, degree)
        return self


    def copy(self):
        """ returns a copy of the Collection"""
        return copy.copy(self)
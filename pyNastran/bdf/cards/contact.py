"""
Defines the following contact cards:

 - BCONP
 - BLSEG
 - BCRPARA
 - BCTPARA
 - BCTADD
 - BCTSET
 - BSURF
 - BSURFS
 - BFRIC

"""
from __future__ import annotations
from typing import TYPE_CHECKING

from pyNastran.bdf.cards.base_card import BaseCard, expand_thru_by, _node_ids
from pyNastran.bdf.bdf_interface.assign_type import (
    integer, integer_or_blank, integer_string_or_blank, double_or_blank,
    integer_double_or_blank, string, string_or_blank, string_choice_or_blank, double)
from pyNastran.bdf.field_writer_8 import print_card_8
from pyNastran.bdf.field_writer_16 import print_card_16
if TYPE_CHECKING:  # pragma: no cover
    from pyNastran.bdf.bdf import BDF


class BFRIC(BaseCard):
    """
    Slideline Contact Friction
    Defines frictional properties between two bodies in contact.

    +-------+------+-------+-------+-------+
    |   1   |   2  |   3   |   4   |   5   |
    +=======+======+=======+=======+=======+
    | BFRIC | FID  | FSTIF |       |  MU1  |
    +-------+------+-------+-------+-------+

    """
    type = 'BFRIC'

    @classmethod
    def _init_from_empty(cls):
        friction_id = 1
        mu1 = 0.2
        return BFRIC(friction_id, mu1)

    def __init__(self, friction_id: int, mu1: float, fstiff=None, comment=''):
        """
        Creates a BFRIC card, which defines a frictional contact.

        Parameters
        ----------
        friction_id : int
            Friction identification number.
        mu1 : float
            Coefficient of static friction.
        fstiff : float; default=None
            Frictional stiffness in stick. See Remarks 2 and 3
            Default=automatically selected by the program.

        """
        BaseCard.__init__(self)
        if comment:
            self.comment = comment
        self.friction_id = friction_id
        self.fstiff = fstiff
        self.mu1 = mu1

    @classmethod
    def add_card(cls, card, comment=''):
        friction_id = integer(card, 1, 'friction_id')
        fstiff = double_or_blank(card, 2, 'fstiff')
        #
        mu1 = double(card, 4, 'mu1')
        return BFRIC(friction_id, mu1, fstiff=fstiff, comment='')

    def raw_fields(self):
        list_fields = [
            'BFRIC', self.friction_id, self.fstiff, None, self.mu1]
        return list_fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)

class BLSEG(BaseCard):
    """
    3D Contact Region Definition by Shell Elements (SOLs 101, 601 and 701)

    Defines a 3D contact region by shell element IDs.

    +=======+====+====+======+====+====+=====+====+====+
    |   1   |  2 |  3 |   4  |  5 |  6 |  7  |  8 |  9 |
    +-------+----+----+------+----+----+-----+----+----+
    | BLSEG | ID | G1 |  G2  | G3 | G4 | G5  | G6 | G7 |
    +-------+----+----+------+----+----+-----+----+----+
    | BLSEG | ID | G1 | THRU | G2 | BY | INC |    |    |
    +-------+----+----+------+----+----+-----+----+----+

    """
    type = 'BLSEG'

    @classmethod
    def _init_from_empty(cls):
        line_id = 1
        nodes = [1]
        return BLSEG(line_id, nodes, comment='')

    def __init__(self, line_id, nodes, comment=''):
        if comment:
            self.comment = comment

        self.line_id = line_id
        self.nodes = expand_thru_by(nodes)
        self.nodes_ref = None

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BLSEG card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        line_id = integer(card, 1, 'line_id')
        #: Number (float)
        nfields = card.nfields
        i = 2
        nodes = []
        while i < nfields:
            d = integer_string_or_blank(card, i, 'field_%s' % i)
            if d is not None:
                nodes.append(d)
            i += 1
        return BLSEG(line_id, nodes, comment=comment)

    def cross_reference(self, model: BDF) -> None:
        msg = f', which is required by BLSEG line_id={self.line_id}'
        self.nodes_ref = model.Nodes(self.nodes, msg=msg)

    def uncross_reference(self) -> None:
        msg = f', which is required by BLSEG line_id={self.line_id}'
        self.nodes = self.node_ids
        self.nodes_ref = None

    @property
    def node_ids(self):
        """returns nodeIDs for repr functions"""
        return _node_ids(self, nodes=self.nodes_ref, allow_empty_nodes=False, msg='')

    def raw_fields(self):
        list_fields = ['BLSEG', self.line_id] + self.node_ids
        return list_fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)

class BCBODY(BaseCard):
    """TODO

        | BCBODY | BID     | DIM    | BEHAV  | BSID |  ISTYP | FRIC    | IDSPL  | CONTROL |
        |        | NLOAD   | ANGVEL | DCOS1  | DCOS2|  DCOS3 | VELRB1  | VELRB2 | VELRB3  |
        |        | ADVANCE | SANGLE | COPTB  | USER |        |         |        |         |
        |        | CTYPE   | ISMALL | ITYPE  | IAUG | PENALT | AUGDIST |
        |        | RIGID   | CGID   | NENT   | --- Rigid Body Name --- |
        |        | APPROV  | A      |  N1    | N2       |    N3   |    V1   |    V2   |   V3   |
        |        | RTEMP   | G(temp)|  Tempr | T(Tempr) |         |         |         |        |
        |        | SINK    | G(sink)|  Tsink | T(Tsink) |         |         |         |        |
        |        | GROW    | GF1    |  GF2   |   GF3    | TAB-GF1 | TAB-GF2 | TAB-GF3 |        |
        |        | HEAT    | CFILM  |  TSINK |   CHEAT  | TBODY   | HCV     | HNC     | ITYPE  |
        |        | BNC     | EMISS  |  HBL   |          |         |         |         |        |
    """
    type = 'BCBODY'
    #@classmethod
    #def _init_from_empty(cls):
        #contact_id = 1
        #slave = 2
        #master = 3
        #sfac = 4
        #friction_id = 5
        #ptype = 'cat'
        #cid = 0
        #return BCBODY(contact_id, dim, behav, bsid, istype, fric, idispl, comment='')

    def __init__(self, contact_id, dim, behav, bsid, istype, fric, idispl, comment=''):
        if comment:
            self.comment = comment
        self.contact_id = contact_id
        self.dim = dim
        self.behav = behav
        self.bsid = bsid
        self.istype = istype
        self.fric = fric
        self.idispl = idispl

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCBODY card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        BID (4,1)
           Contact body identification number referenced by BCTABLE, BCHANGE, or
        BCMOVE. (Integer > 0; Required)
        DIM Dimension of body. (Character; Default=3D)
           DIM=2D planar body in x-y plane of the basic coordinate system, composed of 2D
           elements or curves.
           DIM=3D any 3D body composed of rigid surfaces, shell elements or solid
            elements.
        BEHAV (4,8)
           Behavior of curve or surface (Character; Default = DEFORM) DEFORM body is
           deformable, RIGID body is rigid, SYMM body is a symmetry body, ACOUS
           indicates an acoustic body, WORK indicates body is a workpiece, HEAT indicates
           body is a heat-rigid body. See Remark 3. for Rigid Bodies..
        BSID : int
            Identification number of a BSURF, BCBOX, BCPROP or BCMATL entry if
        BEHAV=DEFORM. (Integer > 0)
        ISTYP : int (4,3)
           Check of contact conditions. (Integer > 0; Default = 0)
        ISTYP : int
           is not supported in segment-to-segment contact.
           For a deformable body:
           =0 symmetric penetration, double sided contact.
           =1 unsymmetric penetration, single sided contact. (Integer > 0)
           =2 double-sided contact with automatic optimization of contact constraint
              equations (this option is known as “optimized contact”).
              Notes: single-sided contact (ISTYP=1) with the contact bodies arranged properly
              using the contact table frequently runs much faster than ISTYP=2.
              For a rigid body:
           =0 no symmetry condition on rigid body.
           =1 rigid body is a symmetry plane.
        FRIC : float (6,7)
            Friction coefficient. (Real > 0 or integer; Default = 0)
            If the value is an integer it represents the ID of a TABL3Di.
        IDSPL : int (4,5)
            Set IDSPL=1 to activate the SPLINE (analytical contact) option for a deformable
           body and for a rigid contact surface. Set it to zero or leave blank to not have
           analytical contact. (Integer; Default = 0)

        """
        contact_id = integer(card, 1, 'contact_id')
        dim = string_choice_or_blank(card, 2, 'dim',
                                     ('2D', '3D'),
                                     '3D')

        behav = string_choice_or_blank(card, 3, 'behav',
                                       ('RIGID', 'DEFORM', 'SYMM', 'ACOUS', 'WORK', 'HEAT'),
                                       'DEFORM')
        bsid = integer(card, 4, 'bsid')
        istype = integer_or_blank(card, 5, 'istype', 0)
        fric = double(card, 6, 'fric')
        idispl = integer_or_blank(card, 7, 'idispl', 0)
        return BCBODY(contact_id, dim, behav, bsid, istype, fric, idispl,
                      comment=comment)

    def raw_fields(self):
        list_fields = [
            'BCBODY', self.contact_id, self.dim, self.behav, self.bsid, self.istype, self.fric, self.idispl]
        return list_fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)


class BCONP(BaseCard):
    """
    3D Contact Region Definition by Shell Elements (SOLs 101, 601 and 701)

    Defines a 3D contact region by shell element IDs.

    +-------+----+-------+--------+-----+------+--------+-------+-----+
    |   1   |  2 |   3   |   4    |  5  |   6  |   7    |   8   |  9  |
    +=======+====+=======+========+=====+======+========+=======+=====+
    | BCONP | ID | SLAVE | MASTER |     | SFAC | FRICID | PTYPE | CID |
    +-------+----+-------+--------+-----+------+--------+-------+-----+
    | BCONP | 95 |   10  |   15   |     |  1.0 |   33   |   1   |     |
    +-------+----+-------+--------+-----+------+--------+-------+-----+

    """
    type = 'BCONP'
    @classmethod
    def _init_from_empty(cls):
        contact_id = 1
        slave = 2
        master = 3
        sfac = 4
        friction_id = 5
        ptype = 'cat'
        cid = 0
        return BCONP(contact_id, slave, master, sfac, friction_id, ptype, cid, comment='')

    def __init__(self, contact_id, slave, master, sfac, friction_id, ptype, cid, comment=''):
        if comment:
            self.comment = comment

        self.contact_id = contact_id
        self.slave = slave
        self.master = master
        self.sfac = sfac
        self.friction_id = friction_id
        self.ptype = ptype
        self.cid = cid
        self.cid_ref = None
        self.friction_id_ref = None
        self.slave_ref = None
        self.master_ref = None

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCONP card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        contact_id = integer(card, 1, 'contact_id')
        slave = integer(card, 2, 'slave')
        master = integer(card, 3, 'master')
        sfac = double_or_blank(card, 5, 'sfac', 1.0)
        friction_id = integer_or_blank(card, 6, 'fric_id')
        ptype = integer_or_blank(card, 7, 'ptype', 1)
        cid = integer_or_blank(card, 8, 'cid', 0)
        return BCONP(contact_id, slave, master, sfac, friction_id, ptype, cid,
                     comment=comment)

    def cross_reference(self, model: BDF) -> None:
        msg = f', which is required by BCONP line_id={self.contact_id}'
        #self.nodes_ref = model.Nodes(self.nodes, msg=msg)
        self.cid_ref = model.Coord(self.cid, msg=msg)
        if self.friction_id is not None:
            self.friction_id_ref = model.bfric[self.friction_id]
        self.slave_ref = model.blseg[self.slave]
        self.master_ref = model.blseg[self.master]

    def uncross_reference(self) -> None:
        self.cid = self.Cid()
        self.friction_id = self.FrictionId()
        self.cid_ref = None
        self.friction_id_ref = None
        self.slave_ref = None
        self.master_ref = None

    def Cid(self) -> int:
        if self.cid_ref is not None:
            return self.cid_ref.cid
        return self.cid

    def FrictionId(self) -> int:
        if self.friction_id_ref is not None:
            return self.friction_id_ref.friction_id
        return self.friction_id

    def Slave(self) -> int:
        if self.slave_ref is not None:
            return self.slave_ref.line_id
        return self.slave

    def Master(self) -> int:
        if self.master_ref is not None:
            return self.master_ref.line_id
        return self.master

    def raw_fields(self):
        list_fields = [
            'BCONP', self.contact_id, self.Slave(), self.Master(), None, self.sfac,
            self.FrictionId(), self.ptype, self.Cid()]
        return list_fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)


class BSURF(BaseCard):
    """
    3D Contact Region Definition by Shell Elements (SOLs 101, 601 and 701)

    Defines a 3D contact region by shell element IDs.

    +-------+------+------+-------+-------+--------+------+------+------+
    |   1   |   2  |   3  |   4   |   5   |    6   |  7   |   8  |   9  |
    +=======+======+======+=======+=======+========+======+======+======+
    | BSURF |  ID  | EID1 | EID2  | EID3  |  EID4  | EID5 | EID6 | EID7 |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       | EID8 | EID9 | EID10 |  etc. |        |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    | BSURF |  ID  | EID1 |  THRU | EID2  |   BY   | INC  |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       | EID8 | EID9 | EID10 | EID11 |  etc.  |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       | EID8 | THRU | EID9  |  BY   |  INC   |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    | BSURF |  15  |  5   | THRU  |  21   |   BY   |  4   |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       |  27  |  30  |  32   |  33   |        |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       |  35  | THRU |  44   |       |        |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+
    |       |  67  |  68  |  70   |  85   |   92   |      |      |      |
    +-------+------+------+-------+-------+--------+------+------+------+

    """
    type = 'BSURF'

    @classmethod
    def _init_from_empty(cls):
        sid = 1
        eids = [1]
        return BSURF(sid, eids, comment='')

    def __init__(self, sid, eids, comment=''):
        if comment:
            self.comment = comment
        #: Set identification number. (Unique Integer > 0)
        self.sid = sid
        #: Element identification numbers of shell elements. (Integer > 0)
        self.eids = eids

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BSURF card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        sid = integer(card, 1, 'sid')
        #: Number (float)
        nfields = card.nfields
        i = 2
        eid_data = []
        while i < nfields:
            d = integer_string_or_blank(card, i, 'field_%s' % i)
            if d is not None:
                eid_data.append(d)
            i += 1
        eids = expand_thru_by(eid_data)
        return BSURF(sid, eids, comment=comment)

    def raw_fields(self):
        fields = ['BSURF', self.sid]
        return fields + list(self.eids)

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)


class BSURFS(BaseCard):
    """
    Defines a 3D contact region by the faces of the CHEXA, CPENTA or CTETRA
    elements.

    Notes
    -----
    1. The continuation field is optional.
    2. BSURFS is a collection of one or more element faces on solid elements.
       BSURFS defines a contact region which may act as a contact source
       (contactor) or target.
    3. The ID must be unique with respect to all other BSURFS, BSURF, and
       BCPROP entries.

    """
    type = 'BSURFS'

    @classmethod
    def _init_from_empty(cls):
        bsurfs_id = 1
        eids = [1]
        g1s = [1]
        g2s = [1]
        g3s = [1]
        return BSURFS(bsurfs_id, eids, g1s, g2s, g3s, comment='')

    def __init__(self, bsurfs_id, eids, g1s, g2s, g3s, comment=''):
        if comment:
            self.comment = comment
        #: Identification number of a contact region. See Remarks 2 and 3.
        #: (Integer > 0)
        self.id = bsurfs_id

        #: Element identification numbers of solid elements. (Integer > 0)
        self.eids = eids

        #: Identification numbers of 3 corner grid points on the face (triangular
        #: or quadrilateral) of the solid element. (Integer > 0)
        self.g1s = g1s
        self.g2s = g2s
        self.g3s = g3s

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BSURFS card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        bsurfs_id = integer(card, 1, 'id')
        eids = []
        g1s = []
        g2s = []
        g3s = []

        n = card.nfields - 5
        i = 0
        j = 1
        while i < n:
            eid = integer(card, 5 + i, 'eid%s' % j)
            g1 = integer(card, 5 + i + 1, 'g3_%s' % j)
            g2 = integer(card, 5 + i + 2, 'g2_%s' % j)
            g3 = integer(card, 5 + i + 3, 'g1_%s' % j)
            j += 1
            i += 4
            eids.append(eid)
            g1s.append(g1)
            g2s.append(g2)
            g3s.append(g3)
        return BSURFS(bsurfs_id, eids, g1s, g2s, g3s, comment=comment)

    def raw_fields(self):
        fields = ['BSURFS', self.id, None, None, None]
        for eid, g1, g2, g3 in zip(self.eids, self.g1s, self.g2s, self.g3s):
            fields += [eid, g1, g2, g3]
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        return self.comment + print_card_8(card)


class BCTSET(BaseCard):
    """
    3D Contact Set Definition (SOLs 101, 601 and 701 only)
    Defines contact pairs of a 3D contact set.

    +--------+-------+------+-------+-------+-------+-------+
    |   1    |   2   | 3    |  4    |   5   |   6   |   7   |
    +========+=======+======+=======+=======+=======+=======+
    | BCTSET | CSID  | SID1 | TID1  | FRIC1 | MIND1 | MAXD1 |
    +--------+-------+------+-------+-------+-------+-------+
    |        |       | SID2  | TID2 | FRIC2 | MIND2 | MAXD2 |
    +--------+-------+------+-------+-------+-------+-------+
    |        |  etc. |      |       |       |       |       |
    +--------+-------+------+-------+-------+-------+-------+

    """
    type = 'BCTSET'

    @classmethod
    def _init_from_empty(cls):
        csid = 1
        sids = [1]
        tids = [1]
        frictions = [0.01]
        min_distances = [0.1]
        max_distances = [1.]
        return BCTSET(csid, sids, tids, frictions, min_distances, max_distances, comment='', sol=101)

    def __init__(self, csid, sids, tids, frictions, min_distances, max_distances,
                 comment='', sol=101):
        if comment:
            self.comment = comment
        #: CSID Contact set identification number. (Integer > 0)
        self.csid = csid
        #: SIDi Source region (contactor) identification number for contact pair i.
        #: (Integer > 0)
        self.sids = sids

        #: TIDi Target region identification number for contact pair i. (Integer > 0)
        self.tids = tids

        #: FRICi Static coefficient of friction for contact pair i. (Real; Default=0.0)
        self.frictions = frictions

        #: MINDi Minimum search distance for contact. (Real) (Sol 101 only)
        self.min_distances = min_distances

        #: MAXDi Maximum search distance for contact. (Real) (Sol 101 only)
        self.max_distances = max_distances

    @classmethod
    def add_card(cls, card, comment='', sol=101):
        csid = integer(card, 1, 'csid')
        sids = []
        tids = []
        frictions = []
        min_distances = []
        max_distances = []

        nfields = card.nfields
        i = 2
        j = 1
        while i < nfields:
            sids.append(integer(card, i, 'sid%s' % j))
            tids.append(integer(card, i + 1, 'tid%s' % j))
            frictions.append(double_or_blank(card, i + 2, 'fric%s' % j, 0.0))
            if sol == 101:
                min_distances.append(double_or_blank(card, i + 3, 'mind%s' % j, 0.0))
                max_distances.append(double_or_blank(card, i + 4, 'maxd%s' % j, 0.0))
            else:
                min_distances.append(None)
                max_distances.append(None)
            i += 8
            j += 1
        return BCTSET(csid, sids, tids, frictions, min_distances,
                      max_distances, comment=comment,
                      sol=sol)

    def raw_fields(self):
        fields = ['BCTSET', self.csid]
        for sid, tid, fric, mind, maxd in zip(self.sids, self.tids, self.frictions,
                                              self.min_distances, self.max_distances):
            fields += [sid, tid, fric, mind, maxd, None, None, None]
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)


class BCRPARA(BaseCard):
    """
    +---------+------+------+--------+------+-----+---+---+---+----+
    |    1    |   2  |   3  |   4    |   5  |  6  | 7 | 8 | 9 | 10 |
    +=========+======+======+========+======+=====+===+===+===+====+
    | BCRPARA | CRID | SURF | OFFSET | TYPE | GP  |   |   |   |    |
    +---------+------+------+--------+------+-----+---+---+---+----+
    """
    type = 'BCRPARA'

    @classmethod
    def _init_from_empty(cls):
        crid = 1
        return BCRPARA(crid, offset=None, surf='TOP', Type='FLEX', grid_point=0, comment='')

    def __init__(self, crid, offset=None, surf='TOP', Type='FLEX', grid_point=0,
                 comment=''):
        """
        Creates a BCRPARA card

        Parameters
        ----------
        crid : int
            CRID Contact region ID.
        offset : float; default=None
            Offset distance for the contact region (Real > 0.0).
            None : OFFSET value in BCTPARA entry
        surf : str; default='TOP'
            SURF Indicates the contact side. See Remark 1.  {'TOP', 'BOT'; )
        Type : str; default='FLEX'
            Indicates whether a contact region is a rigid surface if it
            is used as a target region. {'RIGID', 'FLEX'}.
            This is not supported for SOL 101.
        grid_point : int; default=0
            Control grid point for a target contact region with TYPE=RIGID
            or when the rigid-target algorithm is used.  The grid point
            may be used to control the motion of a rigid surface.
            (Integer > 0).  This is not supported for SOL 101.
        comment : str; default=''
            a comment for the card

        """
        if comment:
            self.comment = comment

        #: CRID Contact region ID. (Integer > 0)
        self.crid = crid

        #: SURF Indicates the contact side. See Remark 1. (Character = "TOP" or
        #: "BOT"; Default = "TOP")
        self.surf = surf

        #: Offset distance for the contact region. See Remark 2. (Real > 0.0,
        #: Default =OFFSET value in BCTPARA entry)
        self.offset = offset

        #: Indicates whether a contact region is a rigid surface if it is used as a
        #: target region. See Remarks 3 and 4. (Character = "RIGID" or "FLEX",
        #: Default = "FLEX"). This is not supported for SOL 101.
        self.Type = Type

        #: Control grid point for a target contact region with TYPE=RIGID or
        #: when the rigid-target algorithm is used. The grid point may be
        #: used to control the motion of a rigid surface. (Integer > 0)
        #: This is not supported for SOL 101.
        self.grid_point = grid_point

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCRPARA card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        crid = integer(card, 1, 'crid')
        surf = string_or_blank(card, 2, 'surf', 'TOP')
        offset = double_or_blank(card, 3, 'offset', None)
        Type = string_or_blank(card, 4, 'type', 'FLEX')
        grid_point = integer_or_blank(card, 5, 'grid_point', 0)
        return BCRPARA(crid, surf=surf, offset=offset, Type=Type,
                       grid_point=grid_point, comment=comment)

    def raw_fields(self):
        fields = ['BCRPARA', self.crid, self.surf, self.offset, self.Type, self.grid_point]
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)


class BCPARA(BaseCard):
    """
    Defines contact parameters used in SOL 600.

    +--------+---------+--------+--------+--------+--------+---------+--------+
    |   1    |    2    |    3   |   4    |   5    |   6    |    7    |    8   |
    +========+=========+========+========+========+========+=========+========+
    | BCPARA |  CSID   | Param1 | Value1 | Param2 | Value2 | Param3  | Value3 |
    +--------+---------+--------+--------+--------+--------+---------+--------+
    |        | Param4  | Value4 | Param5 | Value5 |  etc.  |         |        |
    +--------+---------+--------+--------+--------+--------+---------+--------+
    | BCPARA | NBODIES |   4    |  BIAS  |   0.5  |        |         |        |
    +--------+---------+--------+--------+--------+--------+---------+--------+

    """
    type = 'BCPARA'

    @classmethod
    def _init_from_empty(cls):
        csid = 1
        params = {'NBODIES' : 4}
        return BCTPARM(csid, params, comment='')

    def _finalize_hdf5(self, encoding):
        """hdf5 helper function"""
        keys, values = self.params
        self.params = {key : value for key, value in zip(keys, values)}

    def __init__(self, csid, params, comment=''):
        """
        Creates a BCPARA card

        Parameters
        ----------
        csid : int
            ID is not used and should be set to zero. Only one BCPARA should be
            entered and it applies to all subcases.
        csid : int
            Contact set ID. Parameters defined in this command apply to
            contact set CSID defined by a BCTSET entry. (Integer > 0)
        params : dict[key] : int/float
            the optional parameters
        comment : str; default=''
            a comment for the card

        """
        if comment:
            self.comment = comment

        #: Contact set ID. Parameters defined in this command apply to
        #: contact set CSID defined by a BCTSET entry. (Integer > 0)
        self.csid = csid
        self.params = params

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCPARA card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        csid = integer(card, 1, 'csid')
        i = 2
        j = 1
        params = {}
        while i < card.nfields:
            param = string(card, i, f'param{j}')
            i += 1
            if param == 'FTYPE':
                value = integer_or_blank(card, i, f'value{j}', 1)
                assert value in [6], f'FTYPE must be [6]; FTYPE={value}'
            else:
                raise NotImplementedError(param)

            params[param] = value
            i += 1
            j += 1
            if j == 4:
                i += 1
        return BCPARA(csid, params, comment=comment)

    def raw_fields(self):
        fields = ['BCPARA', self.csid]
        i = 0
        for key, value in sorted(self.params.items()):
            if i == 3:
                fields.append(None)
                i = 0
            fields.append(key)
            fields.append(value)
            i += 1
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)


class BCTPARM(BaseCard):
    """
    Contact Parameters (SOLs 101, 103, 111, 112, and 401).
    Control parameters for the contact algorithm.

    +---------+--------+--------+--------+--------+--------+---------+--------+
    |    1    |   2    |    3   |   4    |   5    |   6    |    7    |    8   |
    +=========+========+========+========+========+========+=========+========+
    | BCTPARM | CSID   | Param1 | Value1 | Param2 | Value2 | Param3  | Value3 |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    |         | Param4 | Value4 | Param5 | Value5 |  etc.  |         |        |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    | BCTPARM |   1    | PENN   |  10.0  |  PENT  |  0.5   |   CTOL  | 0.001  |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    |         | SHLTHK |   1    |        |        |        |         |        |
    +---------+--------+--------+--------+--------+--------+---------+--------+

    """
    type = 'BCTPARM'

    @classmethod
    def _init_from_empty(cls):
        csid = 1
        params = {'CSTIFF' : 1}
        return BCTPARM(csid, params, comment='')

    def _finalize_hdf5(self, encoding):
        """hdf5 helper function"""
        keys, values = self.params
        self.params = {key : value for key, value in zip(keys, values)}

    def __init__(self, csid, params, comment=''):
        """
        Creates a BCTPARM card

        Parameters
        ----------
        csid : int
            Contact set ID. Parameters defined in this command apply to
            contact set CSID defined by a BCTSET entry. (Integer > 0)
        params : dict[key] : value
            the optional parameters
        comment : str; default=''
            a comment for the card

        """
        if comment:
            self.comment = comment

        #: Contact set ID. Parameters defined in this command apply to
        #: contact set CSID defined by a BCTSET entry. (Integer > 0)
        self.csid = csid
        self.params = params

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCTPARM card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        csid = integer(card, 1, 'csid')
        i = 2
        j = 1
        params = {}
        while i < card.nfields:
            param = string(card, i, 'param%s' % j)
            i += 1
            if param == 'TYPE' and 0:
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1, 2], 'TYPE must be [0, 1, 2]; TYPE=%r' % value
            elif param == 'PENN':
                #PENN 10.0
                value = double(card, i, 'value%s' % j)
            elif param == 'PENT':
                #PENT 0.5
                value = double(card, i, 'value%s' % j)
            elif param == 'CTOL':
                #CTOL 10.0
                value = double(card, i, 'value%s' % j)
            elif param == 'SHLTHK':
                #SHLTHK 1
                value = integer(card, i, 'value%s' % j)
            #elif param == 'TYPE': # NX
                #value = string_or_blank(card, i, 'value%s' % j, 'FLEX').upper()
                #assert value in ['FLEX', 'RIGID', 'COATING'], 'TYPE must be [FLEX, RIGID, COATING.]; CSTIFF=%r' % value

            #elif param == 'NSIDE':
                #value = integer_or_blank(card, i, 'value%s' % j, 1)
                #assert value in [1, 2], 'NSIDE must be [1, 2]; NSIDE=%r' % value
            #elif param == 'TBIRTH':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)
            #elif param == 'TDEATH':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)
            #elif param == 'INIPENE':
                #value = integer_or_blank(card, i, 'value%s' % j, 0)
                #assert value in [0, 1, 2, 3], 'INIPENE must be [0, 1, 2]; INIPENE=%r' % value
            #elif param == 'PDEPTH':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)
            #elif param == 'SEGNORM':
                #value = integer_or_blank(card, i, 'value%s' % j, 0)
                #assert value in [-1, 0, 1], 'SEGNORM must be [-1, 0, 1]; SEGNORM=%r' % value
            #elif param == 'OFFTYPE':
                #value = integer_or_blank(card, i, 'value%s' % j, 0)
                #assert value in [0, 1, 2], 'OFFTYPE must be [0, 1, 2]; OFFTYPE=%r' % value
            #elif param == 'OFFSET':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)
            #elif param == 'TZPENE':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)

            #elif param == 'CSTIFF':
                #value = integer_or_blank(card, i, 'value%s' % j, 0)
                #assert value in [0, 1], 'CSTIFF must be [0, 1]; CSTIFF=%r' % value
            #elif param == 'TIED':
                #value = integer_or_blank(card, i, 'value%s' % j, 0)
                #assert value in [0, 1], 'TIED must be [0, 1]; TIED=%r' % value
            #elif param == 'TIEDTOL':
                #value = double_or_blank(card, i, 'value%s' % j, 0.0)
            #elif param == 'EXTFAC':
                #value = double_or_blank(card, i, 'value%s' % j, 0.001)
                #assert 1.0E-6 <= value <= 0.1, 'EXTFAC must be 1.0E-6 < EXTFAC < 0.1; EXTFAC=%r' % value
            else:
                # FRICMOD, FPARA1/2/3/4/5, EPSN, EPST, CFACTOR1, PENETOL
                # NCMOD, TCMOD, RFORCE, LFORCE, RTPCHECK, RTPMAX, XTYPE
                # ...
                value = integer_double_or_blank(card, i, 'value%s' % j)
                assert value is not None, '%s%i must not be None' % (param, j)

            params[param] = value
            i += 1
            j += 1
            if j == 4:
                i += 1
        return BCTPARM(csid, params, comment=comment)

    def raw_fields(self):
        fields = ['BCTPARM', self.csid]
        i = 0
        for key, value in sorted(self.params.items()):
            if i == 3:
                fields.append(None)
                i = 0
            fields.append(key)
            fields.append(value)
            i += 1
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)

class BCTPARA(BaseCard):
    """
    Defines parameters for a surface-to-surface contact region.

    +---------+--------+--------+--------+--------+--------+---------+--------+
    |    1    |   2    |    3   |   4    |   5    |   6    |    7    |    8   |
    +=========+========+========+========+========+========+=========+========+
    | BCTPARA | CSID   | Param1 | Value1 | Param2 | Value2 | Param3  | Value3 |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    |         | Param4 | Value4 | Param5 | Value5 |  etc.  |         |        |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    | BCTPARA |   1    | TYPE   |   0    | NSIDE  |   2    | SEGNORM |  -1    |
    +---------+--------+--------+--------+--------+--------+---------+--------+
    |         | CSTIFF |   1    | OFFSET | 0.015  |        |         |        |
    +---------+--------+--------+--------+--------+--------+---------+--------+

    """
    type = 'BCTPARA'

    @classmethod
    def _init_from_empty(cls):
        csid = 1
        params = {'CSTIFF' : 1}
        return BCTPARA(csid, params, comment='')

    def _finalize_hdf5(self, encoding):
        """hdf5 helper function"""
        keys, values = self.params
        self.params = {key : value for key, value in zip(keys, values)}

    def __init__(self, csid, params, comment=''):
        """
        Creates a BCTPARA card

        Parameters
        ----------
        csid : int
            Contact set ID. Parameters defined in this command apply to
            contact set CSID defined by a BCTSET entry. (Integer > 0)
        params : dict[key] : value
            the optional parameters
        comment : str; default=''
            a comment for the card

        """
        if comment:
            self.comment = comment

        #: Contact set ID. Parameters defined in this command apply to
        #: contact set CSID defined by a BCTSET entry. (Integer > 0)
        self.csid = csid
        self.params = params

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCTPARA card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        csid = integer(card, 1, 'csid')
        i = 2
        j = 1
        params = {}
        while i < card.nfields:
            param = string(card, i, f'param{j}')
            i += 1
            if param == 'TYPE':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1, 2], 'TYPE must be [0, 1, 2]; TYPE=%r' % value
            #elif param == 'TYPE': # NX
                #value = string_or_blank(card, i, 'value%s' % j, 'FLEX').upper()
                #assert value in ['FLEX', 'RIGID', 'COATING'], 'TYPE must be [FLEX, RIGID, COATING.]; CSTIFF=%r' % value

            elif param == 'NSIDE':
                value = integer_or_blank(card, i, 'value%s' % j, 1)
                assert value in [1, 2], 'NSIDE must be [1, 2]; NSIDE=%r' % value
            elif param == 'TBIRTH':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)
            elif param == 'TDEATH':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)
            elif param == 'INIPENE':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1, 2, 3], 'INIPENE must be [0, 1, 2]; INIPENE=%r' % value
            elif param == 'PDEPTH':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)
            elif param == 'SEGNORM':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [-1, 0, 1], 'SEGNORM must be [-1, 0, 1]; SEGNORM=%r' % value
            elif param == 'OFFTYPE':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1, 2], 'OFFTYPE must be [0, 1, 2]; OFFTYPE=%r' % value
            elif param == 'OFFSET':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)
            elif param == 'TZPENE':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)

            elif param == 'CSTIFF':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1], 'CSTIFF must be [0, 1]; CSTIFF=%r' % value
            elif param == 'TIED':
                value = integer_or_blank(card, i, 'value%s' % j, 0)
                assert value in [0, 1], 'TIED must be [0, 1]; TIED=%r' % value
            elif param == 'TIEDTOL':
                value = double_or_blank(card, i, 'value%s' % j, 0.0)
            elif param == 'EXTFAC':
                value = double_or_blank(card, i, 'value%s' % j, 0.001)
                assert 1.0E-6 <= value <= 0.1, 'EXTFAC must be 1.0E-6 < EXTFAC < 0.1; EXTFAC=%r' % value
            else:
                # FRICMOD, FPARA1/2/3/4/5, EPSN, EPST, CFACTOR1, PENETOL
                # NCMOD, TCMOD, RFORCE, LFORCE, RTPCHECK, RTPMAX, XTYPE
                # ...
                value = integer_double_or_blank(card, i, 'value%s' % j)
                assert value is not None, '%s%i must not be None' % (param, j)

            params[param] = value
            i += 1
            j += 1
            if j == 4:
                i += 1
        return BCTPARA(csid, params, comment=comment)

    def raw_fields(self):
        fields = ['BCTPARA', self.csid]
        i = 0
        for key, value in sorted(self.params.items()):
            if i == 3:
                fields.append(None)
                i = 0
            fields.append(key)
            fields.append(value)
            i += 1
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)


class BCTADD(BaseCard):
    """
    +--------+------+----+-------+----+----+----+----+----+
    |   1    |  2   | 3  |   4   |  5 | 6  |  7 | 8  |  9 |
    +========+======+====+=======+====+====+====+====+====+
    | BCTADD | CSID | SI |  S2   | S3 | S4 | S5 | S6 | S7 |
    +--------+------+----+-------+----+----+----+----+----+
    |        |  S8  | S9 |  etc. |    |    |    |    |    |
    +--------+------+----+-------+----+----+----+----+----+

    Remarks:
    1. To include several contact sets defined via BCTSET entries in a model,
       BCTADD must be used to combine the contact sets. CSID in BCTADD is
       then selected with the Case Control command BCSET.
    2. Si must be unique and may not be the identification of this or any other
       BCTADD entry.

    """
    type = 'BCTADD'

    @classmethod
    def _init_from_empty(cls):
        csid = 1
        contact_sets = [1, 2]
        return BCTADD(csid, contact_sets, comment='')

    def __init__(self, csid, contact_sets, comment=''):
        if comment:
            self.comment = comment
        #: Contact set identification number. (Integer > 0)
        self.csid = csid

        #: Identification numbers of contact sets defined via BCTSET entries.
        #: (Integer > 0)
        self.contact_sets = contact_sets

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BCTADD card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        csid = integer(card, 1, 'csid')
        contact_sets = []

        i = 1
        j = 1
        while i < card.nfields:
            contact_set = integer(card, i, 'S%i' % j)
            contact_sets.append(contact_set)
            i += 1
            j += 1
        return BCTADD(csid, contact_sets, comment=comment)

    def raw_fields(self):
        fields = ['BCTADD'] + self.contact_sets
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)

class BGADD(BaseCard):
    """
    +-------+------+----+-------+----+----+----+----+----+
    |   1   |  2   | 3  |   4   |  5 | 6  |  7 | 8  |  9 |
    +=======+======+====+=======+====+====+====+====+====+
    | BGADD | GSID | SI |  S2   | S3 | S4 | S5 | S6 | S7 |
    +-------+------+----+-------+----+----+----+----+----+
    |       |  S8  | S9 |  etc. |    |    |    |    |    |
    +-------+------+----+-------+----+----+----+----+----+

    """
    type = 'BGADD'

    @classmethod
    def _init_from_empty(cls):
        glue_id = 1
        contact_sets = [1, 2]
        return BGADD(glue_id, contact_sets, comment='')

    def __init__(self, glue_id, contact_sets, comment=''):
        if comment:
            self.comment = comment
        #: Glue identification number. (Integer > 0)
        self.glue_id = glue_id

        #: Identification numbers of contact sets defined via BCTSET entries.
        #: (Integer > 0)
        self.contact_sets = contact_sets

    @classmethod
    def add_card(cls, card, comment=''):
        """
        Adds a BGADD card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        glue_id = integer(card, 1, 'glue_id')
        contact_sets = []

        i = 1
        j = 1
        while i < card.nfields:
            contact_set = integer(card, i, 'S%i' % j)
            contact_sets.append(contact_set)
            i += 1
            j += 1
        return BGADD(glue_id, contact_sets, comment=comment)

    def raw_fields(self):
        fields = ['BGADD'] + self.contact_sets
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)

class BGSET(BaseCard):
    """
    +-------+------+------+------+---------+----+------+------+----+
    |   1   |  2   |  3   |   4  |    5    | 6  |  7   |   8  |  9 |
    +=======+======+======+======+=========+====+======+======+====+
    | BGSET | GSID | SID1 | TID1 | SDIST1  |    | EXT1 |      |    |
    +-------+------+------+------+---------+----+------+------+----+
    |       |      | SID2 | TID2 | SDIST2  |    | EXT2 |      |    |
    +-------+------+------+------+---------+----+------+------+----+
    """
    type = 'BGSET'

    @classmethod
    def _init_from_empty(cls):
        glue_id = 1
        sids = [1]
        tids = [1]
        sdists = [0.01]
        exts = [1.]
        return BGSET(glue_id, sids, tids, sdists, exts, comment='', sol=101)

    def __init__(self, glue_id, sids, tids, sdists, exts,
                 comment='', sol=101):
        if comment:
            self.comment = comment
        #: GSID Glue set identification number. (Integer > 0)
        self.glue_id = glue_id
        #: SIDi Source region (contactor) identification number for contact pair i.
        #: (Integer > 0)
        self.sids = sids

        #: TIDi Target region identification number for contact pair i. (Integer > 0)
        self.tids = tids

        #: SDISTi Search distance for glue regions (Real); (Default=10.0)
        self.sdists = sdists

        #: EXTi Extension factor for target region (SOLs 402 and 601 only).
        self.exts = exts

    @classmethod
    def add_card(cls, card, comment='', sol=101):
        glue_id = integer(card, 1, 'glue_id')
        sids = []
        tids = []
        sdists = []
        exts = []

        nfields = card.nfields
        i = 2
        j = 1
        while i < nfields:
            #SIDi Source region identification number for glue pair i. (Integer > 0)
            #TIDi Target region identification number for glue pair i. (Integer > 0)
            #SDISTi Search distance for glue regions (Real); (Default=10.0)
            #EXTi Extension factor for target region (SOLs 402 and 601 only).

            sids.append(integer(card, i, 'sid%s' % j))
            tids.append(integer(card, i + 1, 'tid%s' % j))
            sdists.append(double_or_blank(card, i + 2, 'fric%s' % j, 0.0))
            #if sol == 101:
            exts.append(double_or_blank(card, i + 3, 'mind%s' % j, 0.0))
            #else:
                #exts.append(None)
            i += 8
            j += 1
        return BGSET(glue_id, sids, tids, sdists, exts,
                     comment=comment, sol=sol)

    def raw_fields(self):
        fields = ['BGSET', self.glue_id]
        for sid, tid, sdist, ext in zip(self.sids, self.tids, self.sdists,
                                              self.exts):
            fields += [sid, tid, sdist, None, ext, None, None, None]
        return fields

    def write_card(self, size: int=8, is_double: bool=False) -> str:
        card = self.repr_fields()
        if size == 8:
            return self.comment + print_card_8(card)
        return self.comment + print_card_16(card)

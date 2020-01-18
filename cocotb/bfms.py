###############################################################################
# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
###############################################################################

import os
import importlib
import re
from cocotb.decorators import bfm_param_int_t

import_info_l = []
export_info_l = []

def register_bfm_type(T, hdl):
    global import_info_l
    global export_info_l

    type_info = BfmTypeInfo(T, hdl, import_info_l.copy(), export_info_l.copy())
    BfmMgr.inst().add_type_info(T, type_info)
    import_info_l = []
    export_info_l = []

def register_bfm_import_info(info):
    info.id = len(import_info_l)
    import_info_l.append(info)

def register_bfm_export_info(info):
    info.id = len(export_info_l)
    export_info_l.append(info)

def bfm_hdl_path(py_file, template):
    return os.path.join(
        os.path.dirname(os.path.abspath(py_file)),
        template)

class BfmMethodParamInfo():
    '''
    Information about a single BFM-method parameter
    '''

    def __init__(self, pname, ptype):
        self.pname = pname
        self.ptype = ptype

class BfmMethodInfo():
    '''
    Information about a single BFM method
    - Method type
    - User-specified parameter signature
    '''

    def __init__(self, T, signature):
        fullname = T.__qualname__
        fi = T.__code__

        self.T = T
        self.signature = []
        self.type_info = []
        self.id = -1

        locals_idx = fullname.find("<locals>")
        if locals_idx != -1:
            fullname = fullname[locals_idx+len("<locals>."):]

        if fullname.find('.') == -1:
            raise Exception("Attempting to register a global method as a BFM method")

        args = fi.co_varnames[1:fi.co_argcount]
        if len(signature) != len(args):
            raise Exception("Wrong number of parameter-type elements: expect " + str(len(args)) + " but received " + str(len(signature)))


        for a,t in zip(args, signature):
            self.signature.append(BfmMethodParamInfo(a, t))
            try:
                import simulator
            except Exception:
                # When we're not running in simulation, don't
                # worry about being able to access constants from simulation
                self.type_info.append(None)
            else:
                if isinstance(t, bfm_param_int_t):
                    if t.s:
                        self.type_info.append(simulator.BFM_SI_PARAM)
                    else:
                        self.type_info.append(simulator.BFM_UI_PARAM)

class BfmTypeInfo():

    def __init__(self, T, hdl, import_info, export_info):
        self.T = T
        self.hdl = hdl
        self.import_info = import_info
        self.export_info = export_info

class BfmInfo():

    def __init__(self, bfm, id, inst_name, type_info):
        self.bfm = bfm
        self.id = id
        self.inst_name = inst_name
        self.type_info = type_info

    def call_method(self, method_id, params):
        self.type_info.export_info[method_id].T(
            self.bfm, *params)

class BfmMgr():

    _inst = None

    def __init__(self):
        self.bfm_l = []
        self.bfm_type_info_m = {}
        self.m_initialized = False

    def add_type_info(self, T, type_info):
        self.bfm_type_info_m[T] = type_info

    @staticmethod
    def get_bfms():
        return BfmMgr.inst().bfm_l

    @staticmethod
    def find_bfm(path_pattern):
        inst = BfmMgr.inst()
        bfm = None

        path_pattern_re = re.compile(path_pattern)

        # Find the BFM instance that matches the specified pattern
        matches = (
            b
            for b in inst.bfm_l
            if path_pattern_re.match(b.bfm_info.inst_name)
        )

        return next(matches, None)

    @staticmethod
    def inst():
        if BfmMgr._inst is None:
            BfmMgr._inst = BfmMgr()

        return BfmMgr._inst

    def load_bfms(self):
        '''
        Obtain the list of BFMs from the native layer
        '''
        import simulator
        n_bfms = simulator.bfm_get_count()
        for i in range(n_bfms):
            info = simulator.bfm_get_info(i)
            instname = info[0]
            clsname = info[1]
            try:
                pkgname, clsleaf = clsname.rsplit('.',1)
            except ValueError:
                raise Exception("Incorrectly-formatted BFM class name {!r}".format(clsname))

            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                raise Exception("Failed to import BFM package {!r}".format(pkgname))

            if not hasattr(pkg, clsleaf):
                raise Exception("Failed to find BFM class \"" + clsleaf + "\" in package \"" + pkgname + "\"")

            bfmcls = getattr(pkg, clsleaf)

            type_info = self.bfm_type_info_m[bfmcls]

            bfm = bfmcls()
            bfm_info = BfmInfo(
                bfm,
                len(self.bfm_l),
                instname,
                type_info)
            # Add
            setattr(bfm, "bfm_info", bfm_info)

            self.bfm_l.append(bfm)

    @staticmethod
    def init():
        import simulator
        inst = BfmMgr.inst()
        if not inst.m_initialized:
            simulator.bfm_set_call_method(BfmMgr.call)
            BfmMgr.inst().load_bfms()
            inst.m_initialized = True

    @staticmethod
    def call(
            bfm_id,
            method_id,
            params):
        inst = BfmMgr.inst()
        bfm = inst.bfm_l[bfm_id]

        if not hasattr(bfm, "bfm_info"):
            raise AttributeError("BFM object does not contain 'bfm_info' field")

        bfm.bfm_info.call_method(method_id, params)
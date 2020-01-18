###############################################################################
# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
###############################################################################
import os
import argparse
import importlib
from string import Template

import cocotb
from cocotb.bfms import BfmMgr


def bfm_load_modules(module_l): 
    for m in module_l:
        try:
            importlib.import_module(m)
        except Exception as e:
            print("Error: failed to load module \"" + str(m) + "\": " + str(e))
            raise e

def process_template_vl(template, info):
    """Process a single BFM-HDL template file string (template), 
    substituting generated interface tasks and task-call demux
    based on BFM task declarations (info). Returns complete
    BFM Verilog module as a string"""

    t = Template(template)
    
    bfm_import_calls = ""
    for i in range(len(info.import_info)):
        imp = info.import_info[i]
        bfm_import_calls += "              " + str(i) + ": begin\n"
        bfm_import_calls += "                  " + imp.T.__name__  + "(\n"
        for pi in range(len(imp.signature)):
            p = imp.signature[pi]
            if p.ptype.s:
                bfm_import_calls += "                      $cocotb_bfm_get_param_i32(bfm_id)"
            else:
                bfm_import_calls += "                      $cocotb_bfm_get_param_ui32(bfm_id)"
            
            if pi+1 < len(imp.signature):
                bfm_import_calls += ","
            bfm_import_calls += "\n"
        bfm_import_calls += "                      );\n"
        bfm_import_calls += "              end\n"
        
    bfm_export_tasks = ""
    for i in range(len(info.export_info)):
        exp = info.export_info[i]
        bfm_export_tasks += "    task " + exp.T.__name__ 
        
        if len(exp.signature) > 0:
            bfm_export_tasks += "("
            for j in range(len(exp.signature)):
                p = exp.signature[j]
                bfm_export_tasks += p.ptype.vl_type() + " " + p.pname
                if j+1 < len(exp.signature):
                    bfm_export_tasks += ", "
            bfm_export_tasks += ");\n"
        else:
            bfm_export_tasks += ";\n"
        bfm_export_tasks += "    begin\n"
        bfm_export_tasks += "        $cocotb_bfm_begin_msg(bfm_id, " + str(i) + ");\n"
        for p in exp.signature:
            if p.ptype.s:
                bfm_export_tasks += "        $cocotb_bfm_add_param_si(bfm_id, " + p.pname + ");\n"
            else:
                bfm_export_tasks += "        $cocotb_bfm_add_param_ui(bfm_id, " + p.pname + ");\n"
            
        bfm_export_tasks += "        $cocotb_bfm_end_msg(bfm_id);\n"
        bfm_export_tasks += "    end\n"
        bfm_export_tasks += "    endtask\n"
        
    
    impl_param_m = {
        "bfm_classname" : info.T.__module__ + "." + info.T.__qualname__,
        "bfm_import_calls" : bfm_import_calls,
        "bfm_export_tasks" : bfm_export_tasks
        }
    
    cocotb_bfm_api_impl = """
    reg signed[31:0]      bfm_id;
    event                 bfm_ev;
    reg signed[31:0]      bfm_msg_id;
    
${bfm_export_tasks}
    
    initial begin
      bfm_id = $cocotb_bfm_register("${bfm_classname}", bfm_ev);
      
      while (1) begin
          bfm_msg_id = $cocotb_bfm_claim_msg(bfm_id);
          
          case (bfm_msg_id)
${bfm_import_calls}
              -1: begin
                  @(bfm_ev);
              end
          endcase
          
      end
    end
    """
   
    param_m = {
        "cocotb_bfm_api_impl" : Template(cocotb_bfm_api_impl).safe_substitute(impl_param_m)
        }
    
    
    return t.safe_substitute(param_m)

def bfm_generate_vl(args):
    inst = BfmMgr.inst()
    
    with open(args.o, "w") as out:
        out.write("//***************************************************************************\n")
        out.write("//* BFMs file for cocotb. \n")
        out.write("//* Note: This file is generated by cocotb-bfmgen. Do Not Edit\n")
        out.write("//***************************************************************************\n")

        for t in inst.bfm_type_info_m.keys():
            info = inst.bfm_type_info_m[t]
        
            if cocotb.bfm_vlog not in info.hdl.keys():
                raise Exception("BFM {!r} does not support Verilog".format(t.__name__))
        
            with open(info.hdl[cocotb.bfm_vlog], "r") as template_f:
                template = template_f.read()
        
            out.write(process_template_vl(template, info))
        
def process_template_sv(template, bfm_name, info):
    """Process a single BFM-HDL template file string (template), 
    substituting generated interface tasks and task-call demux
    based on BFM task declarations (info). Returns complete
    BFM SystemVerilog module as a string"""
        
    t = Template(template)
    
    bfm_import_calls = ""
    for i in range(len(info.import_info)):
        imp = info.import_info[i]
        bfm_import_calls += "              " + str(i) + ": begin\n"
        # Verilator doesn't evaluate expressions in the order that
        # they appear in the argument list. Consequently, we need 
        # to create temporary variables to ensure the order is correct.
        for pi in range(len(imp.signature)):
            p = imp.signature[pi]
            if p.ptype.s:
                bfm_import_calls += "                  longint p" + str(pi) + " = cocotb_bfm_get_si_param(bfm_id);\n"
            else:
                bfm_import_calls += "                  longint unsigned p" + str(pi) + " = cocotb_bfm_get_ui_param(bfm_id);\n"
                
        bfm_import_calls += "                  " + imp.T.__name__  + "(\n"
        for pi in range(len(imp.signature)):
            bfm_import_calls += "                      p" + str(pi)

            if pi+1 < len(imp.signature):
                bfm_import_calls += ","
            bfm_import_calls += "\n"
        bfm_import_calls += "                      );\n"
        bfm_import_calls += "              end\n"
        
    bfm_export_tasks = ""
    for i in range(len(info.export_info)):
        exp = info.export_info[i]
        bfm_export_tasks += "    task " + exp.T.__name__ + "("
        for j in range(len(exp.signature)):
            p = exp.signature[j]
            bfm_export_tasks += p.ptype.vl_type() + " " + p.pname
            if j+1 < len(exp.signature):
                bfm_export_tasks += ", "
        bfm_export_tasks += ");\n"
        bfm_export_tasks += "    begin\n"
        bfm_export_tasks += "        cocotb_bfm_begin_msg(bfm_id, " + str(i) + ");\n"
        for p in exp.signature:
            if p.ptype.s:
                bfm_export_tasks += "        cocotb_bfm_add_si_param(bfm_id, " + p.pname + ");\n"
            else:
                bfm_export_tasks += "        cocotb_bfm_add_ui_param(bfm_id, {});\n".format(p.pname)
            
        bfm_export_tasks += "        cocotb_bfm_end_msg(bfm_id);\n"
        bfm_export_tasks += "    end\n"
        bfm_export_tasks += "    endtask\n"
        
    
    impl_param_m = {
        "bfm_name" : bfm_name,
        "bfm_classname" : info.T.__module__ + "." + info.T.__qualname__,
        "bfm_import_calls" : bfm_import_calls,
        "bfm_export_tasks" : bfm_export_tasks
        }
    
    cocotb_bfm_api_impl = """
    int          bfm_id;
    
    import "DPI-C" context function int cocotb_bfm_claim_msg(int bfm_id);
    import "DPI-C" context function longint cocotb_bfm_get_si_param(int bfm_id);
    import "DPI-C" context function longint unsigned cocotb_bfm_get_ui_param(int bfm_id);
    import "DPI-C" context function void cocotb_bfm_begin_msg(int bfm_id, int msg_id);
    import "DPI-C" context function void cocotb_bfm_add_si_param(int bfm_id, longint v);
    import "DPI-C" context function void cocotb_bfm_add_ui_param(int bfm_id, longint unsigned v);
    import "DPI-C" context function void cocotb_bfm_end_msg(int bfm_id);
    
    task automatic ${bfm_name}_process_msg();
        int msg_id = cocotb_bfm_claim_msg(bfm_id);
        case (msg_id)
${bfm_import_calls}
        default: begin
            $display("Error: BFM %m received unsupported message with id %0d", msg_id);
            $finish();
        end
        endcase
    endtask
    export "DPI-C" task ${bfm_name}_process_msg;
    import "DPI-C" context function int ${bfm_name}_register(string inst_name);
    
${bfm_export_tasks}
    
    initial begin
      bfm_id = ${bfm_name}_register($sformatf("%m"));
    end
    """
   
    param_m = {
        "cocotb_bfm_api_impl" : Template(cocotb_bfm_api_impl).safe_substitute(impl_param_m)
        }
    
    
    return t.safe_substitute(param_m)

def generate_dpi_c(bfm_name, info):
    template_p = {
        "bfm_name" : bfm_name,
        "bfm_classname" : info.T.__module__ + "." + info.T.__qualname__,
        }
    
    template = """
int ${bfm_name}_process_msg() __attribute__((weak));

// Stub definition to handle the case where a referenced
// BFM type isn't instanced
int ${bfm_name}_process_msg() { }

static void ${bfm_name}_notify_cb(void *user_data) {
    svSetScope(user_data);
    ${bfm_name}_process_msg();
}

int ${bfm_name}_register(const char *inst_name) {
    return cocotb_bfm_register(
        inst_name, 
        \"${bfm_classname}\", 
        &${bfm_name}_notify_cb, 
        svGetScope());
}
"""
    
    return Template(template).safe_substitute(template_p)
       
def bfm_generate_sv(args):
    inst = BfmMgr.inst()
   
    filename_c = args.o
    if filename_c.find('.') != -1:
        filename_c = os.path.splitext(filename_c)[0]
    filename_c += ".c"
    
    with open(args.o, "w") as out_sv:
        with open(filename_c, "w") as out_c:
            out_sv.write("//***************************************************************************\n")
            out_sv.write("//* BFMs file for cocotb. \n")
            out_sv.write("//* Note: This file is generated. Do Not Edit\n")
            out_sv.write("//***************************************************************************\n")

            out_c.write("//***************************************************************************\n")
            out_c.write("//* BFMs DPI interface file for cocotb. \n")
            out_c.write("//* Note: This file is generated. Do Not Edit\n")
            out_c.write("//***************************************************************************\n")
            out_c.write("#include <stdio.h>\n")
            out_c.write("#ifdef __cplusplus\n")
            out_c.write("extern \"C\" {\n")
            out_c.write("#endif\n")
            out_c.write("\n")
            out_c.write("#include \"svdpi.h\"\n")
            out_c.write("typedef void (*cocotb_bfm_notify_f)(void *);\n")
            out_c.write("int cocotb_bfm_register(const char *, const char *, cocotb_bfm_notify_f, void *);\n")

            for t in inst.bfm_type_info_m.keys():
                info = inst.bfm_type_info_m[t]
        
                if cocotb.bfm_vlog not in info.hdl.keys():
                    raise Exception("BFM \"" + t.__name__ + "\" does not support Verilog")
        
                with open(info.hdl[cocotb.bfm_sv], "r") as template_f:
                    template = template_f.read()
        
                bfm_name = os.path.basename(info.hdl[cocotb.bfm_sv])
    
                if bfm_name.find('.') != -1:
                    bfm_name = os.path.splitext(bfm_name)[0]
        
                out_sv.write(process_template_sv(template, bfm_name, info))
                out_c.write(generate_dpi_c(bfm_name, info))
        
            out_c.write("#ifdef __cplusplus\n")
            out_c.write("}\n")
            out_c.write("#endif\n")

def bfm_generate(args):
    """Generate BFM files required for simulation"""
    
    if args.o is None:
        if args.language == "vlog":
            args.o = "cocotb_bfms.v"
        elif args.language == "sv":
            args.o = "cocotb_bfms.sv"
        elif args.language == "vhdl":
            args.o = "cocotb_bfms.vhdl"
            
    if args.language == "vlog":
        bfm_generate_vl(args)
    elif args.language == "sv":
        bfm_generate_sv(args)
    elif args.language == "vhdl":
        raise Exception("VHDL currently unsupported")

    
# def bfm_list(args):
#     inst = BfmMgr.inst()
#     
#     # TODO: implement list command
#     
#     print("inst=" + str(inst))
# 
#     print("Number of keys: " + str(len(inst.bfm_type_info_m.keys())))
#     for t in inst.bfm_type_info_m.keys():
#         print("BFM: \"" + str(t) + "\"")

def main():
    parser = argparse.ArgumentParser(prog="cocotb-bfmgen")
    
    subparser = parser.add_subparsers()
    subparser.required = True
    subparser.dest = 'command'
    generate_cmd = subparser.add_parser("generate")
    generate_cmd.set_defaults(func=bfm_generate)
    generate_cmd.add_argument("-m", action='append')
    generate_cmd.add_argument("-l", "--language", default="vlog")
    generate_cmd.add_argument("-o", default=None)
    
#     list_cmd = subparser.add_parser("list")
#     list_cmd.set_defaults(func=bfm_list)
#     list_cmd.add_argument("-m", action='append')
    
    args = parser.parse_args()
 
    # Ensure the BfmMgr is created
    BfmMgr.inst()
    
    if hasattr(args, 'm') and args.m is not None:
        bfm_load_modules(args.m)
        
    args.func(args)
    
    
if __name__ == "__main__":
    main()

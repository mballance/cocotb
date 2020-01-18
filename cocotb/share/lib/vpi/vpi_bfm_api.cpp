/******************************************************************************
 * Copyright cocotb contributors
 * Licensed under the Revised BSD License, see LICENSE for details.
 * SPDX-License-Identifier: BSD-3-Clause
 ******************************************************************************/

#include "vpi_bfm_api.h"
#include <stdint.h>
#include "vpi_user.h"
#include "cocotb_bfm_api.h"
#include <stdio.h>
#include <string>

/**
 * cocotb_bfm_notify()
 *
 * Callback function called by the BFM to notify that
 * there is a message to be received. In the VPI
 * implementation, this callback notifies the event
 * that the BFM is waiting on.
 */
static void cocotb_bfm_notify(void *notify_ev) {
    s_vpi_value val;

    val.format = vpiIntVal;
    val.value.integer = 1;

    // Signal an event to cause the BFM to wake up
    vpi_put_value((vpiHandle)notify_ev, &val, 0, vpiNoDelay);
}

/**
 * cocotb_bfm_register_tf()
 *
 * Implementation for the $cocotb_bfm_register system function.
 * Registers a new BFM with the system
 */
static int cocotb_bfm_register_tf(char *user_data) {
    // Obtain arguments
    // - cls_name  -- passed in
    // - notify_ev -- passed in
    // - inst_name -- from call scope
    std::string inst_name, cls_name;
    vpiHandle notify_ev = 0;
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle scope_h = vpi_handle(vpiScope, systf_h);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    s_vpi_value val;
    vpiHandle arg;
    int id;

    // Get the instance name from the context
    inst_name = vpi_get_str(vpiFullName, scope_h);

    // Get the Python class name
    arg = vpi_scan(arg_it);
    val.format = vpiStringVal;
    vpi_get_value(arg, &val);
    cls_name = val.value.str;

    // Get the handle to the notify event
    notify_ev = vpi_scan(arg_it);

    vpi_free_object(arg_it);

    (void)id;

    id = cocotb_bfm_register(
            inst_name.c_str(),
            cls_name.c_str(),
            &cocotb_bfm_notify,
            notify_ev
            );

    // Set return value
    val.format = vpiIntVal;
    val.value.integer = id;
    vpi_put_value(systf_h, &val, 0, vpiNoDelay);

    return 0;
}

static int cocotb_bfm_claim_msg_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id, msg_id = -1;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    vpi_free_object(arg_it);

    msg_id = cocotb_bfm_claim_msg(bfm_id);

    // Set return value
    val.format = vpiIntVal;
    val.value.integer = msg_id;
    vpi_put_value(systf_h, &val, 0, vpiNoDelay);

    return 0;
}

static int cocotb_bfm_get_param_i32_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id;
    int64_t pval;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    vpi_free_object(arg_it);

    pval = cocotb_bfm_get_si_param(bfm_id);

    // Set return value
    val.format = vpiIntVal;
    val.value.integer = pval;
    vpi_put_value(systf_h, &val, 0, vpiNoDelay);

    return 0;
}

static int cocotb_bfm_get_param_ui32_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id;
    int64_t pval;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    vpi_free_object(arg_it);

    pval = cocotb_bfm_get_ui_param(bfm_id);

    // Set return value
    val.format = vpiIntVal;
    // TODO: should really use reg?
    val.value.integer = pval;
    vpi_put_value(systf_h, &val, 0, vpiNoDelay);

    return 0;
}

static int cocotb_bfm_begin_msg_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id, msg_id;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    // Get the msg ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    msg_id = val.value.integer;

    vpi_free_object(arg_it);

    cocotb_bfm_begin_msg(bfm_id, msg_id);

    return 0;
}

static int cocotb_bfm_add_param_si_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id;
    int64_t pval = 0;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    // Get the parameter value
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    pval = val.value.integer;

    vpi_free_object(arg_it);

    cocotb_bfm_add_ui_param(bfm_id, pval);

    return 0;
}

static int cocotb_bfm_add_param_ui_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id;
    uint64_t pval = 0;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    // Get the parameter value
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    pval = (uint32_t)val.value.integer;

    vpi_free_object(arg_it);

    cocotb_bfm_add_ui_param(bfm_id, pval);

    return 0;
}

static int cocotb_bfm_end_msg_tf(char *user_data) {
    vpiHandle systf_h = vpi_handle(vpiSysTfCall, 0);
    vpiHandle arg_it = vpi_iterate(vpiArgument, systf_h);
    vpiHandle arg;
    s_vpi_value val;
    int bfm_id;

    // Get the BFM ID
    arg = vpi_scan(arg_it);
    val.format = vpiIntVal;
    vpi_get_value(arg, &val);
    bfm_id = val.value.integer;

    vpi_free_object(arg_it);

    cocotb_bfm_end_msg(bfm_id);

    return 0;
}


void register_bfm_tf(void) {
    s_vpi_systf_data tf_data;


    // cocotb_bfm_register
    tf_data.type = vpiSysFunc;
    tf_data.tfname = "$cocotb_bfm_register";
    tf_data.calltf = &cocotb_bfm_register_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_claim_msg
    tf_data.type = vpiSysFunc;
    tf_data.tfname = "$cocotb_bfm_claim_msg";
    tf_data.calltf = &cocotb_bfm_claim_msg_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_get_param_i32
    tf_data.type = vpiSysFunc;
    tf_data.tfname = "$cocotb_bfm_get_param_i32";
    tf_data.calltf = &cocotb_bfm_get_param_i32_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_get_param_ui32
    tf_data.type = vpiSysFunc;
    tf_data.tfname = "$cocotb_bfm_get_param_ui32";
    tf_data.calltf = &cocotb_bfm_get_param_ui32_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_get_param_i64

    // cocotb_bfm_get_param_ui64

    // cocotb_bfm_begin_msg
    tf_data.type = vpiSysTask;
    tf_data.tfname = "$cocotb_bfm_begin_msg";
    tf_data.calltf = &cocotb_bfm_begin_msg_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_add_param_ui
    tf_data.type = vpiSysTask;
    tf_data.tfname = "$cocotb_bfm_add_param_ui";
    tf_data.calltf = &cocotb_bfm_add_param_ui_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_add_param_si
    tf_data.type = vpiSysTask;
    tf_data.tfname = "$cocotb_bfm_add_param_si";
    tf_data.calltf = &cocotb_bfm_add_param_si_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);

    // cocotb_bfm_add_param_str

    // cocotb_bfm_end_msg
    tf_data.type = vpiSysTask;
    tf_data.tfname = "$cocotb_bfm_end_msg";
    tf_data.calltf = &cocotb_bfm_end_msg_tf;
    tf_data.compiletf = 0;
    tf_data.sizetf = 0;
    tf_data.user_data = 0;
    vpi_register_systf(&tf_data);
}
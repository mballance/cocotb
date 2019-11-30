/******************************************************************************
* Copyright (c) 2013 Potential Ventures Ltd
* Copyright (c) 2013 SolarFlare Communications Inc
* Copyright (c) 2019 Matthew Ballance
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*    * Redistributions of source code must retain the above copyright
*      notice, this list of conditions and the following disclaimer.
*    * Redistributions in binary form must reproduce the above copyright
*      notice, this list of conditions and the following disclaimer in the
*      documentation and/or other materials provided with the distribution.
*    * Neither the name of Potential Ventures Ltd,
*       SolarFlare Communications Inc nor the
*      names of its contributors may be used to endorse or promote products
*      derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
* ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL POTENTIAL VENTURES LTD BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
******************************************************************************/
#include "GpiBfmMsg.h"
#include <string.h>
#include <stdio.h>

GpiBfmMsg::GpiBfmMsg(
		uint32_t 				id,
		int32_t					paramc,
		cocotb_bfm_msg_param_t	*paramv) {
	m_id = id;
	m_idx = 0;
	if (paramc != -1) {
		m_param_l = new cocotb_bfm_msg_param_t[paramc];
		m_param_l_idx = paramc;
		m_param_l_max = paramc;
		for (int i=0; i<paramc; i++) {
			m_param_l[i] = paramv[i];
			if (paramv[i].ptype == GpiBfmParamType_Str) {
				m_str_l.push_back(paramv[i].pval.str);
				m_param_l[i].pval.str = m_str_l.back().c_str();
			}
		}
	} else {
		m_param_l_max = 16;
		m_param_l = new cocotb_bfm_msg_param_t[m_param_l_max];
		m_param_l_idx = 0;
	}
}

GpiBfmMsg::~GpiBfmMsg() {

}

void GpiBfmMsg::add_param_ui(uint64_t p) {
	cocotb_bfm_msg_param_t param;
	param.ptype = GpiBfmParamType_Ui;
	param.pval.ui64 = p;
	add_param(&param);
}

void GpiBfmMsg::add_param_si(int64_t p) {
	cocotb_bfm_msg_param_t param;
	param.ptype = GpiBfmParamType_Si;
	param.pval.i64 = p;
	add_param(&param);
}

void GpiBfmMsg::add_param(const cocotb_bfm_msg_param_t *p) {
	if (m_param_l_idx >= m_param_l_max) {
		// Time to reallocate
		cocotb_bfm_msg_param_t *tmp = m_param_l;
		m_param_l = new cocotb_bfm_msg_param_t[m_param_l_max+16];
		memcpy(m_param_l, tmp, sizeof(cocotb_bfm_msg_param_t)*m_param_l_idx);
		delete [] tmp;
		m_param_l_max += 16;
	}

	m_param_l[m_param_l_idx++] = *p;
}

void GpiBfmMsg::add_param_s(const char *p) {
	cocotb_bfm_msg_param_t param;
	param.ptype = GpiBfmParamType_Si;
	m_str_l.push_back(p);
	param.pval.str = m_str_l.at(m_str_l.size()-1).c_str();
	add_param(&param);
}

const cocotb_bfm_msg_param_t *GpiBfmMsg::get_param() {
	cocotb_bfm_msg_param_t *ret = 0;
	if (m_idx < m_param_l_idx) {
		ret = &m_param_l[m_idx];
		m_idx++;
	}
	return ret;
}

const cocotb_bfm_msg_param_t *GpiBfmMsg::get_param(uint32_t idx) const {
	const cocotb_bfm_msg_param_t *ret = 0;
	if (idx < m_param_l_idx) {
		ret = &m_param_l[idx];
	}
	return ret;
}

uint64_t GpiBfmMsg::get_param_ui() {
	uint64_t ret = 0;
	if (m_idx < m_param_l_idx) {
		ret = m_param_l[m_idx].pval.ui64;
		m_idx++;
	} else {
		fprintf(stdout, "Error: Out-of-bound request\n");
	}
	return ret;
}

int64_t GpiBfmMsg::get_param_si() {
	int64_t ret = 0;
	if (m_idx < m_param_l_idx) {
		ret = m_param_l[m_idx].pval.i64;
		m_idx++;
	}
	return ret;
}

const char *GpiBfmMsg::get_param_str() {
	const char *ret = "";
	if (m_idx < m_param_l_idx) {
		ret = m_param_l[m_idx].pval.str;
		m_idx++;
	}
	return ret;
}


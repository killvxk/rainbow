# This file is part of rainbow 
#
# PyPDM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Copyright 2019 Victor Servant, Ledger SAS

import unicorn as uc
import capstone as cs
from rainbow.rainbow import rainbowBase
from rainbow.color_functions import color


class rainbow_arm(rainbowBase):

    STACK_ADDR = 0x20000000
    STACK = (STACK_ADDR - 0x200, STACK_ADDR + 32)
    INTERNAL_REGS = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "pc", "lr"]
    TRACE_DISCARD = []

    def __init__(self, trace=True, sca_mode=False, local_vars=[]):
        super().__init__(trace, sca_mode)
        self.emu = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM | uc.UC_MODE_THUMB)
        self.disasm = cs.Cs(cs.CS_ARCH_ARM, cs.CS_MODE_ARM | cs.CS_MODE_THUMB)
        self.disasm.detail = True
        self.word_size = 4
        self.endianness = "little"
        self.page_size = self.emu.query(uc.UC_QUERY_PAGE_SIZE)
        self.page_shift = self.page_size.bit_length() - 1
        self.uc_reg = "uc.arm_const.UC_ARM_REG_"
        self.pc = "pc"

        self.stubbed_functions = local_vars
        self.setup(sca_mode)

        self.emu.reg_write(uc.arm_const.UC_ARM_REG_SP, self.STACK_ADDR)
        self.emu.reg_write(uc.arm_const.UC_ARM_REG_FP, self.STACK_ADDR)
        self.emu.reg_write(uc.arm_const.UC_ARM_REG_APSR, 0)  ## ?

    def start(self, begin, end, timeout=0, count=0):
        return self._start(begin, end, timeout, count)

    def return_force(self):
        self["pc"] = self["lr"]

    def block_handler(self, uci, address, size, user_data):
        self.base_block_handler(address)

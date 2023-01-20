# Copyright 2023 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import json
from typing import List

from .step import TclStep, get_script_dir
from .state import DesignFormat, Output, State


class Synthesis(TclStep):
    outputs = [Output(DesignFormat.NETLIST)]

    def get_command(self) -> List[str]:
        return ["yosys", "-c", self.get_script_path()]

    def get_script_path(self):
        return os.path.join(get_script_dir(), "yosys", "synthesize.tcl")

    def run(
        self,
        **kwargs,
    ) -> State:
        state_out = super().run(**kwargs)

        stats_file = os.path.join(self.step_dir, "reports", "stat.json")
        stats_str = open(stats_file).read()
        stats = json.loads(stats_str)

        state_out.metrics["design__instance__count"] = stats["design"]["num_cells"]
        if chip_area := stats["design"].get("area"):  # needs nonzero area
            state_out.metrics["design__instance__area"] = chip_area

        return state_out

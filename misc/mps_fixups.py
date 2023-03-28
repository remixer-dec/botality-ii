# Workarounds and fixes for LLMs for mps accelerator
# Copyright Jeremy Barnes / MIT License
# reference code:
# https://github.com/jeremybarnes/llm-webgpu/blob/main/mps_fixups.py
#
import torch
from torch import Tensor
from typing import Optional

def fixup_mps():

    orig_topk = torch.topk
    # Topk only works up to k=15 on MPS, replace it with a CPU fallback
    def _topk(self: torch.Tensor, k: int, dim:int=-1, largest:bool=True, sorted:bool=True):
        res, indices = orig_topk(self.to('cpu', torch.float32), k, dim, largest, sorted)
        return res.to(self), indices.to('mps')

    torch.topk = _topk

    orig_max = torch.max
    # Max doesn't work with longs on MPS, replace it with a CPU fallback
    def _max(self: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        return orig_max(self.to('cpu'), *args, **kwargs).to('mps')

    torch.max = _max

    orig_cumsum = torch.cumsum
    # Cumulative sum doesn't work, replace with CPU fallback
    def _cumsum(input: torch.Tensor, dim: int, **kwargs) -> torch.Tensor:
        return orig_cumsum(input.to('cpu', torch.float32), dim, **kwargs).to('mps', input.dtype)

    torch.cumsum = _cumsum
    torch.Tensor.cumsum = _cumsum
    
import torch
from typing import Any, Callable, Optional, Union

from pytorch_lightning.metrics.metric import Metric


class MeanAbsoluteError(Metric):
    """
    Computes mean absolute error.

    Args:
        compute_on_step:
            Forward only calls ``update()`` and return None if this is set to False. default: True
        ddp_sync_on_step:
            Synchronize metric state across processes at each ``forward()``
            before returning the value at the step. default: False
        process_group:
            Specify the process group on which synchronization is called. default: None (which selects the entire world)

    Example:

        >>> from pytorch_lightning.metrics import MeanAbsoluteError
        >>> target = torch.tensor([3.0, -0.5, 2.0, 7.0])
        >>> preds = torch.tensor([2.5, 0.0, 2.0, 8.0])
        >>> mean_absolute_error = MeanAbsoluteError()
        >>> mean_absolute_error(preds, target)
        tensor(0.5000)
    """

    def __init__(
        self,
        compute_on_step: bool = True,
        ddp_sync_on_step: bool = False,
        process_group: Optional[Any] = None,
    ):
        super().__init__(
            compute_on_step=compute_on_step,
            ddp_sync_on_step=ddp_sync_on_step,
            process_group=process_group,
        )

        self.add_state("sum_abs_error", default=torch.tensor(0.0), dist_reduce_fx="sum")
        self.add_state("total", default=torch.tensor(0), dist_reduce_fx="sum")

    def update(self, preds: torch.Tensor, target: torch.Tensor):
        """
        Update state with predictions and targets.

        Args:
            preds: Predictions from model
            target: Ground truth values
        """
        assert preds.shape == target.shape, \
            'Predictions and targets are expected to have the same shape'
        abs_error = torch.abs(preds - target)

        self.sum_abs_error += torch.sum(abs_error)
        self.total += target.numel()

    def compute(self):
        """
        Computes mean absolute error over state.
        """
        return self.sum_abs_error / self.total

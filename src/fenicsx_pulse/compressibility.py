import abc
from dataclasses import dataclass, field

import dolfinx
import ufl

from . import exceptions


class Compressibility(abc.ABC):
    """Base class for compressibility models."""

    @abc.abstractmethod
    def strain_energy(self, J: ufl.core.expr.Expr) -> ufl.core.expr.Expr:
        """Strain energy density function"""
        pass

    def register(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def is_compressible(self) -> bool:
        """Returns True if the material model is compressible."""
        pass


@dataclass(slots=True)
class Incompressible(Compressibility):
    r"""Incompressible material model

    Strain energy density function is given by

    .. math::
        \Psi = p (J - 1)

    """

    p: dolfinx.fem.Function = field(default=None, init=False)

    def __str__(self) -> str:
        return "p (J - 1)"

    def register(self, p: dolfinx.fem.Function) -> None:
        self.p = p

    def strain_energy(self, J: ufl.core.expr.Expr) -> ufl.core.expr.Expr:
        if self.p is None:
            raise exceptions.MissingModelAttribute(attr="p", model=type(self).__name__)
        return self.p * (J - 1.0)

    def is_compressible(self) -> bool:
        return False


@dataclass(slots=True)
class Compressible(Compressibility):
    r"""Compressible material model

    Strain energy density function is given by

    .. math::
        \Psi = \kappa (J \ln(J) - J + 1)

    """

    kappa: float | dolfinx.fem.Function | dolfinx.fem.Constant = 1e3

    def __str__(self) -> str:
        return "\u03ba (J ln(J) - J + 1)"

    def strain_energy(self, J: ufl.core.expr.Expr) -> ufl.core.expr.Expr:
        return self.kappa * (J * ufl.ln(J) - J + 1)

    def is_compressible(self) -> bool:
        return True

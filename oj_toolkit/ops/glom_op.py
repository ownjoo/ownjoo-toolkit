"""Glom: an escape hatch to the third-party glom library's spec language.

dig()/Digger (jmespath) and resolve()/Resolver (attribute/method access) cover most
extraction needs, but neither can express "call this method with real arguments partway
through a path" -- resolve() only auto-calls zero-argument callables it encounters.
glom's T object can (T.get_page(2).items), along with a much larger spec vocabulary
(Coalesce, Check, Fold, ...). Rather than reimplement any of that, Glom just delegates
to glom.glom(item, spec, **kwargs) -- the same role Map(fn) plays for plain callables.

glom is an optional dependency: importing oj_toolkit.ops never requires it, only
constructing a Glom instance does (via a lazy import in __init__). Install it with:
pip install 'oj-toolkit[glom]'
"""

from typing import Any

from oj_toolkit.ops.base import ItemOp
from oj_toolkit.ops.registry import register

_GLOM_INSTALL_HINT = "glom is not installed. Install it with: pip install 'oj-toolkit[glom]'"


@register("glom")
class Glom(ItemOp):
    """Delegate to glom.glom(item, spec, **glom_kwargs).

    Attributes:
        spec: A glom spec -- a jmespath-style dotted string, a dict/list/tuple spec,
            a glom.T path expression, Coalesce(...), Check(...), or anything else
            glom.glom() itself accepts as spec.
        glom_kwargs: Forwarded to glom.glom() as-is (e.g. default=, skip_exc=, scope=).
            Not reinterpreted -- glom's own semantics for each kwarg apply unchanged.
    """

    def __init__(self, spec: Any, **glom_kwargs: Any) -> None:
        try:
            import glom as _glom_module  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(_GLOM_INSTALL_HINT) from exc
        self._glom = _glom_module.glom
        self.spec = spec
        self.glom_kwargs = glom_kwargs

    def __call__(self, item: Any) -> Any:
        return self._glom(item, self.spec, **self.glom_kwargs)

    def clone(self, **overrides: Any) -> "Glom":
        kwargs = {"spec": self.spec, **self.glom_kwargs, **overrides}
        return Glom(**kwargs)

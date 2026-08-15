"""Registry and declarative compiler for ops.

register() maps a string type name to an Op subclass; compile() recursively turns a
JSON/YAML-shaped spec dict into a tree of Op instances using that registry.
"""

from collections.abc import Mapping
from typing import Any, Callable, Type

from oj_toolkit.ops.base import Op

_REGISTRY: dict[str, Type[Op]] = {}


def register(name: str, override: bool = False) -> Callable[[Type[Op]], Type[Op]]:
    """Class decorator: register cls under name for declarative compile().

    Args:
        name: The string type name used in a spec dict's "type" key (e.g. "and", "iter").
        override: If True, allow replacing an already-registered class under name.
            Default: False -- registering a *different* class under a name that's already
            taken raises ValueError. Re-registering the identical class object under the
            same name is always a no-op, regardless of override.

    Returns:
        A decorator that registers cls and returns it unchanged.

    Example:
        >>> @register('greet')
        ... class Greet(Op):
        ...     def __init__(self, name):
        ...         self.name = name
        ...     def __call__(self, arg):
        ...         return f'hello {self.name}'
    """

    def decorator(cls: Type[Op]) -> Type[Op]:
        existing = _REGISTRY.get(name)
        if existing is not None and existing is not cls and not override:
            raise ValueError(
                f"ops type {name!r} is already registered to {existing.__name__}; "
                f"pass register({name!r}, override=True) to replace it intentionally"
            )
        cls.type_name = name
        _REGISTRY[name] = cls
        return cls

    return decorator


def compile(spec: Any) -> Any:  # pylint: disable=redefined-builtin
    """Recursively build an Op tree from a declarative spec.

    Args:
        spec: A Mapping containing a "type" key is compiled into an Op: every OTHER key's
            value is itself recursively compiled, then the registered class is
            instantiated as cls(**resolved_kwargs). A list has each element recursively
            compiled. Anything else -- including a Mapping WITHOUT a "type" key, e.g. a
            Fanout's per-field dict or a dig_many-style paths dict -- is returned
            unchanged (literal passthrough).

    Returns:
        An Op instance, a list of compiled values, or the original literal value.

    Example:
        >>> spec = {'type': 'and', 'ops': [
        ...     {'type': 'in', 'input': 'status', 'value': ['ok', 'warn']},
        ...     {'type': 'not', 'op': {'type': 'exists', 'input': 'error'}},
        ... ]}
        >>> op = compile(spec)  # doctest: +SKIP
    """
    if isinstance(spec, Mapping) and "type" in spec:
        try:
            cls = _REGISTRY[spec["type"]]
        except KeyError as exc:
            raise KeyError(
                f"Unknown ops type {spec['type']!r}. Registered types: {sorted(_REGISTRY)}"
            ) from exc
        kwargs = {k: compile(v) for k, v in spec.items() if k != "type"}
        return cls(**kwargs)
    if isinstance(spec, list):
        return [compile(item) for item in spec]
    return spec

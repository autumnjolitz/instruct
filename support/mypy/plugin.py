from typing import Optional, Callable, List, Type
from dataclasses import dataclass
from mypy.plugin import Plugin
from mypy.plugin import ClassDefContext
from mypy.nodes import AssignmentStmt, NameExpr, Expression, StrExpr, DictExpr, TypeInfo


@dataclass
class Attribute:
    name: str
    types: List[Type]
    node: TypeInfo


class InstructTransformer:
    def __init__(self, ctx: ClassDefContext) -> None:
        self._ctx = ctx

    def transform(self) -> None:
        ctx = self._ctx
        cls = ctx.cls
        info = self._ctx.cls.info
        attributes = self.collect_attributes()

        if ctx.api.options.new_semantic_analyzer:
            # Check if attribute types are ready.
            for attr in attributes:
                if info[attr.name].type is None:
                    ctx.api.defer()
                    return
        # Todo: I want to extract cls.__slots__ and then
        # create a vector of attributes where:
        #     if __slots__ is Tuple[str, ...], then each attribute has an Any type
        #     if __slots__ is a Dict[str, Union[typing.TypeVar, Iterable[typing.TypeVar]]]
        #        then assume there will be a property that accepts
        #       cls._all_coercions[property_name] + values(attribute) in Dict
        print(attributes, cls.name)

    def collect_attributes(self) -> List[Attribute]:
        ctx = self._ctx
        cls = ctx.cls
        attributes = []

        for statement in cls.defs.body:
            if not isinstance(statement, AssignmentStmt):
                continue
            lhs = statement.lvalues[0]
            if not isinstance(lhs, NameExpr):
                continue
            if lhs.name != "__slots__":
                continue
            for name, typeish, node in _collect_args(ctx, statement.rvalue):
                attributes.append(Attribute(name, typeish, node))

        return attributes


def _collect_args(ctx, expr: Expression):
    if isinstance(expr, DictExpr):
        for key, value in expr.items:
            if not isinstance(key, StrExpr):
                ctx.api.fail("Must be a string for the keys", expr)
                return
            if not isinstance(value, NameExpr):
                ctx.api.fail("Must be a typing definition", expr)
                return
            from mypy.checkmember import type_object_type  # To avoid import cycle.

            converter_type = type_object_type(value.node, ctx.api.builtin_type)
            yield key.value, converter_type.items()[0].arg_types, value.node


class InstructPlugin(Plugin):
    def wrap_base(self, ctx: ClassDefContext) -> None:
        transformer = InstructTransformer(ctx)
        print("ass")
        try:
            transformer.transform()
        except Exception as e:
            print(e)

    def get_base_class_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname != "instruct.Base":
            return None
        return self.wrap_base


def plugin(version: str):
    # ignore version argument if the plugin works with all mypy versions.
    return InstructPlugin

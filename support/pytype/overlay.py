from pytype import overlay, abstract


# class InstructOverlay(overlay.Overlay):
#     def __init__(self, vm):
#         assert False, 'havent determined method to load this overlay into'
#         member_map = {
#             'class': InstructClassTypeImpl.make
#         }
#         ast = vm.loader.import_name("instruct")
#         super().__init__(vm, 'instruct', member_map, ast)


# class InstructClassTypeImpl(abstract.PyTDClass):
#     @classmethod
#     def make(cls, name, vm):
#         return super().make(name, vm, 'instruct')

#     def call(self, node, func, args, alias_map=None):
#         assert False, 'needs more work'
#         return super().call(node, func, args, alias_map=alias_map)

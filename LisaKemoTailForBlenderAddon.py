bl_info = {
    "name": "Kemo Tail",
    "author": "michinari.nukazawa@gmail.com",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Add > Mesh > Kemo Tail",
    "description": "Adds a new Mesh Object of Fox Tail (Anime/Manga Like)",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add


# Z軸高さを基準にしてvertices選択する
# 実装はObjectMode版。bmeshを使うとEditModeで実装できるらしいが...?
# select the vertices by z axis position: 
def select_by_z_axis(zaxis, delta = 0.5):
    bpy.ops.object.mode_set(mode="OBJECT")
    target_verts = [vertex for vertex in bpy.context.object.data.vertices if delta > abs(vertex.co[2] - zaxis)]
    for v in target_verts: v.select = True
    bpy.ops.object.mode_set(mode="EDIT")


def add_kemo_tail(
        loc_x = 0, loc_y = 0, loc_z = 0,
        rot_x = 0, rot_y = 0, rot_z = 0, 
        align = "WORLD",
        circle_vertices = 129,
        diameter_scale = 1.15,
        fur_random_seed = 0,
        fur_confluence_level = 0.63,
        fur_twist_level = 1.0
        ):
    # 一応、念の為
    # set EDIT mode's select mode to "vertex select" 
    bpy.context.tool_settings.mesh_select_mode = (True , False , False)

    # this depend only script run in debugging.
    # if exist active object (not append a already exist object in Edit mode)
    # オブジェクトが選択状態でなくても動作するための汚いトリック
    # 本当は存在をチェックしたいが、方法がわからなかったため例外を握りつぶす方法で対処
    # これをしないと、Object選択済みかつEditModeだった場合に、生成した尻尾のverticesが既存Objectと混ざってしまうため
    try: #if bpy.ops.object != None:
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError:
        print('close my eyes')
        # collapse

    bpy.ops.mesh.primitive_circle_add(
            vertices=circle_vertices, align=align,
            location=(loc_x, loc_y, loc_z), scale=(1, 1, 1))

    #bpy.ops.object.name = "Kemo Tail"
    for obj in bpy.context.selected_objects:
        obj.name = "Kemotail"

    bpy.ops.object.mode_set(mode="EDIT")

    # make tail root Step1 (and deside mesh Normal)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, -1)})

    #
    bpy.ops.mesh.select_all(action='DESELECT')
    select_by_z_axis(zaxis = 0)
    bpy.ops.mesh.select_nth(nth=2)
    bpy.ops.transform.resize(value=(diameter_scale, diameter_scale, diameter_scale))

    bpy.ops.mesh.select_all(action='DESELECT')
    select_by_z_axis(zaxis = 0)
    for zaxis in (1.2, 1.8, 2, 2, 1, 1):
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, zaxis)})

    # 毛並みの点を乱すランダムは大きくしすぎると突き抜けるので固定値。
    # TODO 本当は点の数が増えて密集したら対応して度合いを減らさないとやはり突き抜けるのだが。
    # Exclusion Tail root
    select_by_z_axis(zaxis = -1)
    bpy.ops.mesh.hide(unselected=False)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.vertex_random(offset=0.05)
    bpy.ops.mesh.reveal()

    rings = [
        {'zaxis' : 0.0, 'resize' : 0.51, 'collapseNum': 2, 'rotate' : -0.0},
        {'zaxis' : 1.2, 'resize' : 0.76, 'collapseNum': 1, 'rotate' : -0.5},
        {'zaxis' : 3.0, 'resize' : 0.89, 'collapseNum': 1, 'rotate' : -0.9},
        {'zaxis' : 5.0, 'resize' : 0.81, 'collapseNum': 1, 'rotate' : -1.2},
        {'zaxis' : 7.0, 'resize' : 0.56, 'collapseNum': 1, 'rotate' : -0.7},
        {'zaxis' : 8.0, 'resize' : 0.39, 'collapseNum': 2, 'rotate' : -0.6},
        {'zaxis' : 9.0, 'resize' : 0.20, 'collapseNum': 3, 'rotate' : -0.4},
    ]

    # resize rings
    for ring in rings:
        bpy.ops.mesh.select_all(action='DESELECT')
        select_by_z_axis(zaxis = ring['zaxis'])
        bpy.ops.transform.resize(value=(ring['resize'], ring['resize'], 1))

    # collapse rings
    for index, ring in enumerate(rings):
        bpy.ops.mesh.select_all(action='DESELECT')
        select_by_z_axis(zaxis = ring['zaxis'])
        bpy.ops.mesh.hide(unselected=True)
        for i in range(ring['collapseNum']):
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_random(ratio = fur_confluence_level, seed=fur_random_seed)
            fur_random_seed += 1
            bpy.ops.mesh.merge(type='COLLAPSE')
        bpy.ops.mesh.reveal()

    # twist tail
    for ring in rings:
        bpy.ops.mesh.select_all(action='DESELECT')
        select_by_z_axis(zaxis = ring['zaxis'])
        bpy.ops.transform.rotate(value= (ring['rotate'] * fur_twist_level), orient_axis='Z')

    # make tail tip
    bpy.ops.mesh.select_all(action='DESELECT')
    select_by_z_axis(zaxis = 9.0)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 1)})
    bpy.ops.mesh.merge(type='COLLAPSE')

    # make tail root Step2
    # 真円リングが２本になっているのは、ユーザが編集する際にループカット操作ができるようにしておくため。
    bpy.ops.mesh.select_all(action='DESELECT')
    select_by_z_axis(zaxis = 0)
    bpy.ops.transform.resize(value=(1, 1, 0))
    #bpy.ops.transform.translate(value=(0, 0, 0.2), orient_axis_ortho='X')
    #
    rootringscale = rings[0]['resize'] * 0.7
    bpy.ops.mesh.select_all(action='DESELECT')
    select_by_z_axis(zaxis = -1)
    bpy.ops.transform.resize(value=(rootringscale, rootringscale, 1))
    # NOTICE: "TRANSFORM_OT_resize" not exist in API show on Console.
    # https://developer.blender.org/T84148
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})
    bpy.ops.transform.resize(value=(0.7, 0.7, 1))
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})
    bpy.ops.mesh.merge(type='COLLAPSE')
    select_by_z_axis(zaxis = -1)
    bpy.ops.transform.translate(value=(0, 0, 1), orient_axis_ortho='X')

    # Modifier SubdivisionSurface
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 3
    bpy.context.object.modifiers["Subdivision"].render_levels = 3
    
    # rotate by param
    bpy.ops.transform.rotate(value=rot_x, orient_axis='X')
    bpy.ops.transform.rotate(value=rot_y, orient_axis='Y')
    bpy.ops.transform.rotate(value=rot_z, orient_axis='Z')


def add_object(self, context):
    # TODO "Align" is not tested.
    add_kemo_tail(
            self.location.x, self.location.y, self.location.z, 
            self.rotation.x, self.rotation.y, self.rotation.z, 
            self.align,
            self.ring_vertices,
            self.diameter_scale,
            self.fur_random_seed,
            self.fur_confluence_level,
            self.fur_twist_level
            )


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Kemo Tail Mesh Object"""
    bl_idname = "mesh.add_lisa_kemo_tail"
    bl_label = "Add Kemo Tail"
    bl_options = {'REGISTER', 'UNDO'}

    # Hummu... I can't remove auto append Align, Location, Rotation on Panel.
    # Panel: name of “head-up display” panel or Redo Panel
    # https://docs.blender.org/manual/en/2.90/interface/undo_redo.html#adjust-last-operation
    # https://docs.blender.org/api/current/bpy.props.html

    # Notice: FloatProperty.step is 1/100 base
    # https://docs.blender.org/api/current/bpy.types.FloatProperty.html#bpy.types.FloatProperty.step
    ring_vertices: bpy.props.IntProperty(name="Ring Vertices Num", default=129, step=3, min=9, max=2048)
    diameter_scale: bpy.props.FloatProperty(name="Ridge Diameter Scale", default=1.15, step=1.0, min=0.0, max=5.0)
    fur_random_seed: bpy.props.IntProperty(name="Fur Confluence Random Seed", default=0, min=0, max=2048)
    fur_confluence_level: bpy.props.FloatProperty(name="Fur Confluence Level", default=0.63, step=1.0, min=0.0, max=1.0)
    fur_twist_level: bpy.props.FloatProperty(name="Fur Twist Level", default=1.0, step=5.0, min=0.0, max=10.0)

    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    # 本当は独自アイコンを使いたいのだけれど2022年時点でできないような情報があるので試さなかった。
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Kemo Tail",
        icon='PLUGIN')


# This allows you to right click on a button and link to documentation
def add_object_manual_map():
    url_manual_prefix = "https://github.com/MichinariNukazawa/LisaKemoTailForBlenderAddon/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "index.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()

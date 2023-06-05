bl_info = {
    "name": "EASEtool: Selection",
    "author": "Kidney",
    "version": (1, 1, 1),
    "blender": (3, 5, 0),
    "location": "3D View (Alt G)",
    "description": "Different Select Menu and a small vertex group and face map manager",
    "warning": "",
    "doc_url": "",
    "category": "Selection",
}


import bpy, bmesh
from bpy.types import UIList, Menu, Operator, PropertyGroup
from bpy.props import IntProperty, StringProperty, BoolProperty, PointerProperty, EnumProperty


#############################################################
####    PORPERTIES    #######################################
#############################################################

class EASEtool_Selection_Property_Group(PropertyGroup):
    
    vg_name: StringProperty( name = "Name", description = "Name of the new vertex group", default = "Group")
    fm_name: StringProperty( name = "Name", description = "Name of the new face map", default = "FaceMap")


#############################################################
####    LIST    #############################################
#############################################################

class EASEtool_UL_Vertex_Group_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.split(factor = 0.52, align = True)
                row.prop(item, "name", text="", emboss=False,)
                row = row.row(align = True, translate = False)
                
                ## Lock
                icon_lock = "LOCKED" if item.lock_weight else "UNLOCKED"
                row.prop(item, "lock_weight", emboss=False, text="", icon=icon_lock)
                
                ## Select
                op1 = row.operator("easetool.vertex_group_action", emboss=False, text="", icon="RESTRICT_SELECT_OFF")
                ## Deselect
                op2 = row.operator("easetool.vertex_group_action", emboss=False, text="", icon="RESTRICT_SELECT_ON")
                ## Asign
                op3 = row.operator("easetool.vertex_group_action", emboss=False, text="", icon="ADD")
                ## Remove
                op4 = row.operator("easetool.vertex_group_action", emboss=False, text="", icon="REMOVE")
                ## Delete
                op5 = row.operator("easetool.vertex_group_action", emboss=False, text="", icon="TRASH")
                
                index = item.index
                op1.index, op2.index, op3.index, op4.index, op5.index = index, index, index, index, index
                op1.action, op2.action, op3.action, op4.action, op5.action = "SELECT", "DESELECT", "ASSIGN", "REMOVE", "DELETE"
                         
                
            else:
                layout.label(text="", translate=False, icon="GROUP_VERTEX")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            
                        
class EASEtool_UL_Face_Map_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.split(factor=0.65, align = True)
                row.prop(item, "name", text="", emboss=False)
                row = row.row(align = True, translate = False)
                
                ## Select
                op1 = row.operator("easetool.face_map_action", emboss=False, text="", icon="RESTRICT_SELECT_OFF")
                ## Deselect
                op2 = row.operator("easetool.face_map_action", emboss=False, text="", icon="RESTRICT_SELECT_ON")
                ## Asign
                op3 = row.operator("easetool.face_map_action", emboss=False, text="", icon="ADD")
                ## Remove
                op4 = row.operator("easetool.face_map_action", emboss=False, text="", icon="REMOVE")
                ## Delete
                op5 = row.operator("easetool.face_map_action", emboss=False, text="", icon="TRASH")
                
                index = item.index
                op1.index, op2.index, op3.index, op4.index, op5.index = index, index, index, index, index
                op1.action, op2.action, op3.action, op4.action, op5.action = "SELECT", "DESELECT", "ASSIGN", "REMOVE", "DELETE"

            else:
                layout.label(text="", translate=False, icon="FACE_MAPS")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#############################################################
####    OPERATORS    ########################################
#############################################################

class EASEtool_OT_Select_Ngons(Operator):
    """Select ngons, quad, tris"""
    bl_idname = "easetool.select_ngons"
    bl_label = "Select Ngons"
    
    type: EnumProperty( name="Type",
        items=[ ("GREATER", "Ngons", "More than 4"),
        ("EQUAL", "Quads", "4 vertices"),
        ("LESS", "Tris", "3 vertices")],
        )

    def execute(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=4, type=self.type)
              
        return {'FINISHED'}

class EASEtool_OT_Group_Action(Operator):
    """Parent Function for Group actions"""
    bl_idname = "easetool.group_action"
    bl_label = "Group Action"
    
    index: IntProperty( name="Group index", default = 0 )
    action: EnumProperty( name="Operator action",
        items = [ ("SELECT", "Select", "Select group"),
        ("DESELECT", "Deselect", "Deselect group"),
        ("ASSIGN", "Assign", "Assign group"),
        ("REMOVE", "Remove", "Remove group"),
        ("DELETE", "Delete", "Delete group")],
        )
        
        
class EASEtool_OT_Vertex_Group_Action(EASEtool_OT_Group_Action):
    """Select, deselect, remove, assign vertices to vertex groups"""
    bl_idname = "easetool.vertex_group_action"
    bl_label = "Vertex Group Action"
           
    def execute(self, context):        
        # Get the active object
        obj = context.active_object
        # Set the active vertex group index
        obj.vertex_groups.active_index = self.index
        
        if self.action == "SELECT":
            bpy.ops.object.vertex_group_select()
        elif self.action == "DESELECT":
            bpy.ops.object.vertex_group_deselect()
        elif self.action == "ASSIGN":        
            bpy.ops.object.vertex_group_assign()
        elif self.action == "REMOVE":            
            bpy.ops.object.vertex_group_remove_from()
        elif self.action == "DELETE":            
            bpy.ops.object.vertex_group_remove()

        return {'FINISHED'}

class EASEtool_OT_Face_Map_Action(EASEtool_OT_Group_Action):
    """Select, deselect, remove, assign faces to face map"""
    bl_idname = "easetool.face_map_action"
    bl_label = "Face Map Action"
           
    def execute(self, context):
        obj = context.active_object
        obj.face_maps.active_index = self.index
        
        if self.action == "SELECT":
            bpy.ops.object.face_map_select()
        elif self.action == "DESELECT":
            bpy.ops.object.face_map_deselect()
        elif self.action == "ASSIGN":        
            bpy.ops.object.face_map_assign()
        elif self.action == "REMOVE":            
            bpy.ops.object.face_map_remove_from()
        elif self.action == "DELETE":            
            bpy.ops.object.face_map_remove()
              
        return {'FINISHED'}
    
class EASEtool_OT_Vertex_Group_From_Selection(Operator):
    """Make vertex group from selection"""
    bl_idname = "easetool.vertex_group_from_selection"
    bl_label = "New Group From Selection"
    
    name: StringProperty( name = "New Vertex Group Name", description = "Name of the new vertex group", default = "Group")
       
    def execute(self, context):
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign()
        
        obj = context.active_object
        index = obj.vertex_groups.active_index
        active_vertex_group = obj.vertex_groups[index]
        
        active_vertex_group.name = self.name
        
        return {'FINISHED'}

    
class EASEtool_OT_Face_Map_From_Selection(Operator):
    """Make face map from selection"""
    bl_idname = "easetool.face_map_from_selection"
    bl_label = "New Map From Selection"
    
    name: StringProperty( name = "New Vertex Group Name", description = "Name of the new face map", default = "Map")
       
    def execute(self, context):
        bpy.ops.object.face_map_add()
        bpy.ops.object.face_map_assign()
        
        obj = context.active_object
        index = obj.face_maps.active_index
        active_face_map = obj.face_maps[index]
        
        active_face_map.name = self.name
                      
        return {'FINISHED'}
    

class EASEtool_OT_Face_Maps_From_Face_Strength(Operator):
    """Make face map from selection, removes maps with names: 'Weak', 'Medium', 'Strong'"""
    bl_idname = "easetool.face_map_from_face_strength"
    bl_label = "New Maps From Face Strength"
    
    names = ["Weak", "Medium", "Strong"]
       
    def execute(self, context):
        ## remove old
        obj = context.active_object
        face_maps = obj.face_maps
        for n in self.names: ## Loop over names
            face_map = face_maps.get(n, False) ## Get Index if found
            if face_map:
                face_maps.active_index = face_map.index
                bpy.ops.object.face_map_remove() ## Remove

        ## Weak
        bpy.ops.mesh.mod_weighted_strength(set=False, face_strength='WEAK')
        bpy.ops.easetool.face_map_from_selection(name=self.names[0])
        
        ## Menum
        bpy.ops.mesh.mod_weighted_strength(set=False, face_strength='MEDIUM')
        bpy.ops.easetool.face_map_from_selection(name=self.names[1])
       
        ## Strong
        bpy.ops.mesh.mod_weighted_strength(set=False, face_strength='STRONG')
        bpy.ops.easetool.face_map_from_selection(name=self.names[2])
                      
        return {'FINISHED'}
    

class EASEtool_OT_Delete_All_Vertex_Groups(Operator):
    """Delete all vertex groups"""
    bl_idname = "easetool.delete_all_vertex_groups"
    bl_label = "Delete All Vertex Groups"
    bl_icon = "TRASH"
       
    def execute(self, context):
        obj = context.active_object
        vertex_groups = obj.vertex_groups        
        
        for i in range(len(vertex_groups)-1, -1, -1):
            obj.vertex_groups.active_index = i        
            bpy.ops.object.vertex_group_remove()
                      
        return {'FINISHED'}
    
class EASEtool_OT_Delete_All_Face_Maps(Operator):
    """Delete all face maps"""
    bl_idname = "easetool.delete_all_face_maps"
    bl_label = "Delete All Face Maps"
    bl_icon = "TRASH"
       
    def execute(self, context):
        obj = context.active_object
        face_maps = obj.face_maps        

        for i in range(len(face_maps)-1, -1, -1):
            face_maps.active_index = i
            bpy.ops.object.face_map_remove()
                      
        return {'FINISHED'}
        

#############################################################
####    UI    ###############################################
#############################################################
    

class EASEtool_UI_Selection(Operator):
    """UI popup for selection, vertex groups and face maps"""
    bl_idname = "easetool.call_selection_ui"
    bl_label = "EASEtool: Selection"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        ## Do nothing, this operator has no functionality, it only calls the UI
        return {'FINISHED'}

    def invoke(self, context, event):
        ## Call the UI
        wm = context.window_manager
        return wm.invoke_popup(self, width=700)
     
    def draw(self, context):
        
        obj = context.active_object
        scene = context.scene
        props = scene.ease_sel_props
        
        
        layout = self.layout
        layout.label(text=self.bl_label)
        main_row = layout.row()
        
                
        ## Column one
        select_box = main_row.box()
        select_box.ui_units_x = 10
        
        select_box.label(text="Select", icon="RESTRICT_SELECT_OFF")
        
        row = select_box.row()
        
        col = row.column(align=True)        
        col.label(text="Face Strength:")
        op1 = col.operator("mesh.mod_weighted_strength", text="Weak")        
        op2 = col.operator("mesh.mod_weighted_strength", text="Medium")
        op3 = col.operator("mesh.mod_weighted_strength", text="Strong")
        op1.face_strength, op2.face_strength, op3.face_strength = "WEAK", "MEDIUM", "STRONG"
        op1.set, op2.set, op3.set = False, False, False
        
        col = row.column(align=True)
        col.label(text="Geometry:")
        col.operator_enum("easetool.select_ngons", "type")
        
        row = select_box.row()
        
        col = row.column(align=True)
        col.label(text="Linked:")
        col.operator_enum("mesh.select_linked", property="delimit")

        col = row.column(align=True)
        col.label(text="Trait:")
        col.operator("mesh.select_non_manifold", text="Non manifold")
        col.operator("mesh.select_loose", text="Loose Geo")
        col.operator("mesh.select_interior_faces", text="Interior faces")
        col.operator("mesh.select_face_by_sides", text="Faces by sides")
        col.operator("mesh.select_ungrouped", text="Ungrouped")

        col = select_box.column(align=True)
        col.label(text="Similar:")
        col.operator_enum("mesh.select_similar", property="type")
        

        
        ## Column two
        vertex_box = main_row.box()
        vertex_box.ui_units_x = 12
        vertex_box.label(text="Vertex Groups", icon="GROUP_VERTEX")
        
        vertex_groups = obj.vertex_groups
        col = vertex_box.column(translate=False, align=True)
        col.template_list("EASEtool_UL_Vertex_Group_List", "Vertex Groups", obj, "vertex_groups", vertex_groups, "active_index", rows=12, maxrows=12)

        ## Create for selection
        col.separator()
        col.prop(props, "vg_name")        
        col.separator()
        col.prop(scene.tool_settings, "vertex_group_weight", text="Weight")
        col.operator("easetool.vertex_group_from_selection", icon="RESTRICT_SELECT_OFF").name = props.vg_name
        
        ## Delete all            
        col.separator()
        col.operator("easetool.delete_all_vertex_groups", icon="TRASH")
        

        ## Column three        
        face_box = main_row.box()        
        face_box.ui_units_x = 12
        face_box.label(text="Face Maps", icon="FACE_MAPS")
        
        face_maps = obj.face_maps
        col = face_box.column(translate=False, align=True)
        col.template_list("EASEtool_UL_Face_Map_List", "Face maps", obj, "face_maps", face_maps, "active_index", rows=12, maxrows=12)
        
        ## Create from selection
        col.separator()
        col.prop(props, "fm_name")        
        col.separator()
        col.operator("easetool.face_map_from_selection", icon="RESTRICT_SELECT_OFF").name = props.fm_name
        
        ## Group by face strength
        col.operator("easetool.face_map_from_face_strength", icon="MOD_NORMALEDIT")
        
        ## Delete all            
        col.separator()
        col.operator("easetool.delete_all_face_maps", icon="TRASH")

        
        
    
#############################################################
####    REGISTRATION    #####################################
#############################################################

classes = [ EASEtool_UI_Selection, EASEtool_Selection_Property_Group,
            EASEtool_UL_Vertex_Group_List, EASEtool_UL_Face_Map_List,
            EASEtool_OT_Select_Ngons,
            EASEtool_OT_Group_Action, EASEtool_OT_Face_Map_Action, EASEtool_OT_Vertex_Group_Action,
            EASEtool_OT_Vertex_Group_From_Selection, EASEtool_OT_Face_Map_From_Selection, EASEtool_OT_Face_Maps_From_Face_Strength,
            EASEtool_OT_Delete_All_Vertex_Groups, EASEtool_OT_Delete_All_Face_Maps,            
            ]  
addon_keymaps = []



def register_keymaps():
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name="Mesh", space_type="EMPTY")
    kmi = km.keymap_items.new('easetool.call_selection_ui', 'G', 'PRESS', alt = True)
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    
        
from bpy.utils import register_class, unregister_class

def register():
    for c in classes:
        register_class(c)
        
    register_keymaps()
    ## Register properties
    bpy.types.Scene.ease_sel_props = PointerProperty(type = EASEtool_Selection_Property_Group)
        
def unregister():
    for c in classes:
        unregister_class(c)
    
    unregister_keymaps()    
    del bpy.types.Scene.ease_sel_props

if __name__ == "__main__":
    register()
    
#    bpy.ops.easetool.call_selection_ui("INVOKE_DEFAULT")
    
    

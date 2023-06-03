bl_info = {
    "name": "EASEtool: Normal",
    "author": "Kidney",
    "version": (1, 2, 3),
    "blender": (3, 5, 0),
    "location": "3D View (Alt N)",
    "description": "Replacing normal edit menu with a pie menu plus extra tools",
    "warning": "",
    "doc_url": "",
    "category": "Normal",
}





import bpy
from bpy.types import Menu, Operator
from bpy.props import EnumProperty, FloatProperty, StringProperty, BoolProperty, FloatVectorProperty





#######################################################################################################################
##### OPERATORS #####
#######################################################################################################################

class EASEtool_OT_Select_Face_Strength(Operator):
    """Select by face strength"""
    bl_idname = "easetool.select_face_strength"
    bl_label = "Select by Face Strength"
    bl_options = {'REGISTER', 'UNDO'}

    face_strength: EnumProperty(
        items=[("STRONG", "Strong", "Face Strength attribute Strong"),
               ("MEDIUM", "Medium", "Face Strength attribute Medium"),               
               ("WEAK", "Weak", "Face Strength attribute Weak")],
        name="Face Strength"
    )
    
    set = False
    obj = None
        
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    def execute(self, context):        
        # Get the active object in the scene
        self.obj = bpy.context.active_object
        if self.obj is None:
            self.report({'ERROR'}, "No object active")
            return {'CANCELLED'}

        bpy.ops.mesh.mod_weighted_strength(set=self.set, face_strength=self.face_strength)
        return {'FINISHED'}

class EASEtool_OT_Set_Face_Strength(EASEtool_OT_Select_Face_Strength):
    """Set face strength and add a weighted normal modifier"""
    bl_idname = "easetool.set_face_strength"
    bl_label = "Set Face Strength"
    
    def execute(self, context):
        self.set = True
        super().execute(context)
        self.weighted_normal_setup()

        return {'FINISHED'}
    
    def weighted_normal_setup(self):
         # find or create weighted normal
        for mod in self.obj.modifiers:
            if mod.type == 'WEIGHTED_NORMAL':
                return
        else:
            mod = self.obj.modifiers.new("Weighted Normals", 'WEIGHTED_NORMAL')
        mod.use_face_influence = True
        bpy.ops.mesh.faces_shade_smooth()
        self.obj.data.use_auto_smooth = True
        self.obj.data.auto_smooth_angle = 1.0472
        return

class EASEtool_OT_Toggle_Auto_Smooth(Operator):
    """Toggle Auto Smooth"""
    bl_idname = "easetool.toggle_auto_smooth"
    bl_label = "Toggle Auto Smooth"

    def execute(self, context):      
        data = context.object.data
        data.use_auto_smooth = not data.use_auto_smooth

        return {'FINISHED'}
    
class EASEtool_OT_Set_Auto_Smooth_Angle(Operator):
    """Set Auto Smooth Angle"""
    bl_idname = "easetool.set_auto_smooth_angle"
    bl_label = "Set Auto Smooth Angle"
        
    angles: EnumProperty(
        name="Angles", description = "Preset values for autosmooth",
        items=[("30", "30", "30.0", "NUMBER", 0),
            ("60", "60", "60.0", "NUMBER", 1),
            ("90", "90", "90.0", "NUMBER", 2),
            ("180", "180", "180.0", "NUMBER", 3)],
    )
    
    angle: FloatProperty(name="Auto Smooth angle")

    def execute(self, context):
        data = context.object.data
        angle_rad = self.angle * (3.141592653589793 / 180)
        data.auto_smooth_angle = angle_rad

        return {'FINISHED'}
    
class EASEtool_OT_Set_Shade_Mode(Operator):
    """Set Shade Mode or Edge Shading"""
    bl_idname = "easetool.set_shade_mode"
    bl_label = "Set Shade Mode"
    
    mode: EnumProperty(
        items=[("SMOOTH", "Smooth", "Shade Smooth"),
               ("FLAT", "Flat", "Shade Flat")],
        name="Shading Mode"
    )

    def execute(self, context): 
        if bpy.context.mode == "OBJECT":
            if self.mode == "SMOOTH":
                bpy.ops.object.shade_smooth()
            else:
                bpy.ops.object.shade_flat()
        elif bpy.context.mode == "EDIT_MESH":
            if self.mode == "SMOOTH":
                bpy.ops.mesh.faces_shade_smooth()
            else:
                bpy.ops.mesh.faces_shade_flat()
              
        return {'FINISHED'}
    
class EASEtool_OT_Add_Weighted_Normal(Operator):
    """Create Weighted Normal modifier"""
    bl_idname = "easetool.add_weighted_normal"
    bl_label = "Add Weighted Normal Modifier"
    
    keep_sharp: BoolProperty(
        name = "Keep Sharp",
        default = False
    )
    face_influence: BoolProperty(
        name = "Face Influence",
        default = True
    )
    
    def execute(self, context):
        obj = bpy.context.active_object
        mod = obj.modifiers.new("Weighted Normals", 'WEIGHTED_NORMAL')
        mod.keep_sharp = self.keep_sharp
        mod.use_face_influence = self.face_influence
        data = context.object.data
        data.use_auto_smooth = True
        
        return {'FINISHED'}


class EASEtool_OT_Call_Normal_Pie(Operator):
    """Call pie menu. For keymaps"""
    bl_idname = "easetool.call_normal_pie"
    bl_label = "EASEtool: Normal Pie"
    bl_category = "Normal"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="EASETOOL_MT_normal_pie")

        return {'FINISHED'}
    
#######################################################################################################################
##### UI #####
#######################################################################################################################
        
class EASEtool_Normal_Pie_Menu(Menu):
    """Normal Edit tool Pie menu UI"""
    bl_idname = "EASETOOL_MT_normal_pie"
    bl_label = "EASEtool: Normals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Normal"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}
    
    def draw(self, context):
        #current object
        active = context.active_object
        active_data = active.data
#        overlay = context.space_data.overlay
        
        layout = self.layout
        pie = layout.menu_pie()
        # Location order: W, E, S, N, NW, NE, SW, SE

        if active.mode == "EDIT":
            
            box = pie.box() #W
            col = box.column(align=True)
            col.label(text="Set Face Strength")
            col.operator_enum("easetool.set_face_strength", property="face_strength")
        
            box = pie.box() #E
            col = box.column(align=True)
            col.label(text="Select Face Strength")
            col.operator_enum("easetool.select_face_strength", property="face_strength")

            box = pie.box() #S            
            col = box.column(align=True)
            col.label(text="Edge")
            row = col.row(align=True)
            row.operator("mesh.mark_sharp", text="Mark Sharp")
            row.operator("mesh.mark_sharp", text="Clear Sharp").clear=True
            
        else:
            pie.separator() #W
            pie.separator() #E 
            pie.separator() #S  

        ##### MAIN #####
        row_main = pie.row() #N
        
        
        # First Column
        col1 = row_main.column()
        
        # Constom Normals
        box = col1.box()
        r = box.row()
        
        col = r.column(align = True)
        col.operator("mesh.set_normals_from_faces", text="Set from Face")
        # TODO operator flatten faces (set normals only for strong?) 
        col.operator("transform.rotate_normal", text="Rotate Normal")
        col.operator("mesh.point_normals", text="Point to Target") # make point to cursor
        col.operator("mesh.merge_normals", text="Merge")
        col.operator("mesh.split_normals", text="Split")
        col.operator_menu_enum("mesh.average_normals", property="average_type", text="Average")
        
        col = r.column(align = True)
        col.operator_enum("mesh.normals_tools", "mode")
        col.operator("mesh.smooth_normals", text="Smooth Vectors")
#        
#        col = box.column(align = True)
#        col.operator("easetool.set_normal_vector", text="Set Normals")

        if active_data.has_custom_normals:
            col = box.column(align = True)
            col.operator("mesh.customdata_custom_splitnormals_clear", text="Clear Custom Normals")

        # Second Column
        col2 = row_main.column()

        # AutoSmooth
        box = col2.box()
        c = box.column(align=True)
        splitFac = 0.5

        ## This AutoSmooth UI is taken from Machin3 tools addon, because it fit in this context
        row = c.split(factor=splitFac, align=True) # split Smooth/Flat from Autosmooth
        r = row.row(align=True)
        
        r.operator("easetool.set_shade_mode", text="Smooth", icon="MESH_CIRCLE").mode = "SMOOTH"
        r.operator("easetool.set_shade_mode", text="Flat", icon="MESH_CUBE").mode = "FLAT"

        row.prop(active_data, "use_auto_smooth")
        
        row = c.split(factor=splitFac, align=True) # split angle presets from slider
        r = row.row(align=True)        
        row.active = not active_data.has_custom_normals and active_data.use_auto_smooth
        
        angles = [30, 60, 90, 180] # set these later

        for angle in angles: # operator_enum doesn't work with rows
            r.operator("easetool.set_auto_smooth_angle", text=str(angle)).angle=angle

        row.prop(active_data, "auto_smooth_angle")
        
        overlay = context.space_data.overlay # Error if run in Text Editor
        # Normal Vectors
        if active.mode == "EDIT":
            box = col2.box() 
            c = box.column(align=True)
            r = c.split(factor=0.2, align=True)
            r.label(text="Normals")
            
            r = r.row(translate=False, align=True)
            r1 = r.row(align=True)
            
            r1.prop(overlay, "show_vertex_normals", text="", icon='NORMALS_VERTEX')
            r1.prop(overlay, "show_split_normals", text="", icon='NORMALS_VERTEX_FACE')
            r1.prop(overlay, "show_face_normals", text="", icon='NORMALS_FACE')
            
            r = r.row(translate=False, align=True)
            r.prop(overlay, "normals_length")
            r.prop(overlay, "use_normals_constant_screen_size", text="", icon="FIXED_SIZE")
        
        # Display Face Attributes
        box = col2.box()
        col = box.column(align=True)
        r = col.row(align=True)
        
        r.prop(context.space_data.shading, "show_backface_culling")
        r.prop(overlay, "show_face_orientation")

        # Face Oreientation
        r = col.row(align=True)
        r.operator("mesh.normals_make_consistent", text="Recalculate Outside").inside=False        
        r.operator("mesh.normals_make_consistent", text="Recalculate Inside").inside=True
        r.operator("mesh.flip_normals", text="Flip Normals")
        
        # Mark Sharp/Smooth
        ## Moving this to Pie
#        box = col2.box()
#        r = box.split(factor=0.5, align=True)
#        r.operator("mesh.mark_sharp", text="Mark Sharp")
#        r.operator("mesh.mark_sharp", text="Mark Smooth").clear=True
        
#        bpy.ops.mesh.mark_sharp(clear=True)

                
        # Third Column
        col3 = row_main.column()
        
        # Weigted Normals Modifier
        box = col3.box()
        col = box.column(align=True)
            
        wn_mods = []
        # List Weighted Normal Modifiers on Object
        for mod in active.modifiers:
            print(mod)
            if mod.type == 'WEIGHTED_NORMAL':
                wn_mods.append(mod)  
                
        if len(wn_mods) > 0:
            mod = wn_mods[len(wn_mods)-1]
            mod_name = mod.name

            r = col.split(factor=0.1, align=True)
            r.label(icon="MOD_NORMALEDIT")
            r = r.split(factor=0.7, align=True)
            r.prop(mod, "name", text="")
            r.prop(mod, "show_on_cage", text="")
            r.prop(mod, "show_in_editmode", text="") 
            r.prop(mod, "show_viewport", text="")
            r.operator("object.modifier_apply", text="", icon="CHECKMARK").modifier = mod_name      
            r.operator("object.modifier_remove", text="", icon="X").modifier = mod_name
            r = col.split(factor=0.4, align=True)
            r.label(text="Weighting Mode")
            r.prop(mod, "mode", text="")
            col.prop(mod, "weight")
            col.prop(mod, "thresh")
            r = col.split(factor=0.5, align=True)
            r.prop(mod, "keep_sharp")
            r.prop(mod, "use_face_influence")
            r = col.split(factor=0.4, align=True)
            r.label(text="Vertex Group", icon="GROUP_VERTEX")
            r = r.split(factor=0.9, align=True)
            r.prop(mod, "vertex_group", text="")
            r.prop(mod, "invert_vertex_group", text="", icon="ARROW_LEFTRIGHT")
            
        else:
            
            col.operator("easetool.add_weighted_normal", text="Weighted Normal Modifier", icon="MOD_NORMALEDIT").keep_sharp = False
            col.operator("easetool.add_weighted_normal", text="Weighted Normal Modifier (Sharp)", icon="MOD_NORMALEDIT").keep_sharp = True
        
        # Face Strengths
    
        # box = col3.box()
        # col = box.column(align=True)
        # row = col.split(factor=0.2, align=True)

        ## Moving to Pie
#        row.label(text="Select:")
#        row.operator("easetool.select_face_strength", text="Strong").face_strength="STRONG"
#        row.operator("easetool.select_face_strength", text="Medium").face_strength="MEDIUM"
#        row.operator("easetool.select_face_strength", text="Weak").face_strength="WEAK"
#   
#        row = col.split(factor=0.2, align=True)
#        row.label(text="Set:")
#        row.operator("easetool.set_face_strength", text="Strong").face_strength="STRONG"
#        row.operator("easetool.set_face_strength", text="Medium").face_strength="MEDIUM"
#        row.operator("easetool.set_face_strength", text="Weak").face_strength="WEAK"
        
            


#######################################################################################################################
##### REGISTRATION #####
#######################################################################################################################


classes = [ EASEtool_Normal_Pie_Menu, EASEtool_OT_Select_Face_Strength, EASEtool_OT_Set_Face_Strength, EASEtool_OT_Toggle_Auto_Smooth,
            EASEtool_OT_Set_Auto_Smooth_Angle, EASEtool_OT_Set_Shade_Mode, EASEtool_OT_Add_Weighted_Normal,
            EASEtool_OT_Call_Normal_Pie,
            ]
addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('easetool.call_normal_pie', 'N', 'PRESS', alt=True)
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    # wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

def register():
    for c in classes:
        bpy.utils.register_class(c)

    register_keymaps()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    unregister_keymaps()


if __name__ == "__main__":
    register()

#    bpy.ops.wm.call_menu_pie(name="EASETOOL_MT_normal_pie")

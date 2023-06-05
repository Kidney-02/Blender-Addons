bl_info = {
    "name": "EASEtool: Materials",
    "author": "Kidney",
    "version": (1, 0, 2),
    "blender": (3, 5, 0),
    "location": "3D View > Sidebar",
    "description": "Material panel for managing materials in blender file",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}

import bpy
from bpy.types import UIList, Panel, Operator, PropertyGroup
from bpy.props import IntProperty, StringProperty, BoolProperty, PointerProperty, FloatVectorProperty, EnumProperty
from random import random, uniform
import colorsys

#############################################################
####    PROPERTIES    #######################################
#############################################################

class EASEtool_Material_Property_Group(PropertyGroup):
    ## List Index
    material_index: IntProperty( name = "Material List Index", description = "Index of selected material in EASEtool material list", default = 0)
    
    ## Remove Material From Object    
    delete_slot: BoolProperty( name = "Delete Material Slot", description = "Delete material slot of removed materials", default = False)
    
    ## Delete Unused Material Slots
    keep_original: BoolProperty( name = "Keep Original Selection", description = "Keep original selection after removing material slots from all", default = True)
    
    ## Add Material To Selection
    overwrite_original: BoolProperty( name = "Overwrite Original Materials", description = "Remove old material slots after adding selected", default = False)
    to_end: BoolProperty( name = "Add the material to the end of the list", description = "Append material to the end of the objects material list", default = False)
    
    ## Create Material
    random_color: BoolProperty( name = "Random Color", description = "Make material with random color", default = False)
    new_name: StringProperty( name = "Name", description = "Name of new material", default = "Material")
    new_color: FloatVectorProperty( name="Color", description = "Color of new material", subtype='COLOR', size=4, 
        default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0)
    new_shader: EnumProperty( name = "Shader Type", description = "Shader of new material",
        items=[("ShaderNodeBsdfPrincipled", "Principled BSDF", 'principled'),
        ("ShaderNodeBsdfDiffuse", "Diffuse BSDF", 'diffuse'),
        ("ShaderNodeEmission", "Emission", 'emission'),
        ("ShaderNodeBsdfGlossy", "Glossy BSDF", 'glossy'),
        ("ShaderNodeBsdfTransparent", "Transparent BSDF", 'transparent'),
        ("ShaderNodeBsdfGlass", "Glass BSDF", 'glass'),
        ("ShaderNodeBackground", "Background", 'background')],

        
        default = "ShaderNodeBsdfPrincipled")
    
    

#############################################################
####    LIST    #############################################
#############################################################

class EASEtool_UL_Material_List(UIList):
        
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):              
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row(translate=False)
                row.prop(item, "name", text="", emboss=False, icon_value=icon)
                
                material = bpy.data.materials.get(item.name)
                row = row.row(translate=False, align = True)
                row.alignment = 'RIGHT'
                row.label(text=str(material.users))
                row.prop(material, "use_fake_user", text="", emboss=False)
                
                props = context.scene.ease_mat_prop_grp
                
                ## Add material to selection
                op1 = row.operator("easetool.add_material", emboss=False, text="", icon="ADD")
                op1.selected_only = True
                op1.overwrite = props.overwrite_original
                op1.to_end = props.to_end
                ## Remove from selection
                op2 = row.operator("easetool.remove_material", emboss=False, text="", icon="REMOVE")
                op2.selected_only = True
                op2.delete_slot = props.delete_slot
                ## Delete from file
                op3 = row.operator("easetool.delete_materials", emboss=False, text="", icon="TRASH")
                op3.delete_all = False
                op1.index, op2.index, op3.index = index ,index, index
            else:
                layout.label(text="", translate=False, icon_value=icon)
                
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
 
#############################################################
####   FUNCTIONS    #########################################
#############################################################            
            
def get_objects(selected: bool) -> []:
    """
    get objects list
    selected - get selected or all in scene
    """
    if selected:
        return bpy.context.selected_objects
    else:
        ## All objects that can have a material
        material_object_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'CURVES', 'POINTCLOUD', 'VOLUME', 'GPENCIL'}
        return [obj for obj in bpy.context.scene.objects if obj.type in material_object_types]  

def any_materials() -> bool:
    return len(bpy.data.materials) > 0



#############################################################
####   OPERATORS    #########################################
#############################################################

class EASEtool_OT_Delete_Materials(Operator):
    """Delete material from file"""
    bl_idname = "easetool.delete_materials"
    bl_label = "Delete Materials"
    
    @classmethod
    def poll(cls, context):
        ## Check if there are any materials in the blend file
        return any_materials()
    
    index: IntProperty( name = "Index", default = 0)
    delete_all: BoolProperty( name = "Delete All", default=False)
        
    def execute(self, context):
        # Get the list of materials
        materials = bpy.data.materials
        
        if self.delete_all: ## if delete_all don't need to check for index, just remove all and return
            context.scene.ease_mat_prop_grp.material_index = 0
            for i in range(len(materials) -1, -1, -1):
                materials.remove(materials[i])
                
            return {'FINISHED'}
        
        ## if not delete_all execute rest of the code
        ## Check if index provided
        index = self.index
        
        if index > -1: ## If Out of range don't delete anything, not sure this is the best, but it seems reasonable
            context.scene.ease_mat_prop_grp.material_index -= 1
            materials.remove(materials[index])
                    
            
        return {'FINISHED'}
                
                
class EASEtool_OT_Delete_Unused_Materials(Operator):
    """Delete orphan materials"""
    bl_idname = "easetool.delete_unused_materials"
    bl_label = "Delete Unsuded Material from File"
    
    @classmethod
    def poll(cls, context):
        # Check if there are any materials in the blend file
        return any_materials()
        
    def execute(self, context):
        ## Set Index to 0 to avoid index out of range error
        context.scene.ease_mat_prop_grp.material_index = 0
        
        materials = bpy.data.materials
        ## Loop Material List
        for i in range(len(materials) -1, -1, -1):
            ## If users == 0 remove
            if materials[i].users == 0:
               materials.remove(materials[i])
               
        return {'FINISHED'}
               

class EASEtool_OT_Remove_Material(Operator):
    """Remove material from selected objects or all"""
    bl_idname = "easetool.remove_material"
    bl_label = "Remove Material"
    
    @classmethod
    def poll(cls, context):
        # Check if there are any materials in the blend file
        return any_materials()
    
    index: IntProperty( name = "Index", default = -1 )
    delete_slot: BoolProperty( name = "Delete Material Slot", default = False)
    selected_only: BoolProperty( name = "Only Affect Active", default = True)
               
    def execute(self, context):

        # Get the list of materials
        materials = bpy.data.materials
        
        ## Check if index is given
        index = self.index
                
        material = materials[index]
        
        objects = get_objects(self.selected_only)
        
        # Get the number of material slots
               
        for obj in objects:
            ## loop backwards to check so you can remove the slots
            num_slots = len(obj.material_slots)
            materials = obj.data.materials
            for i in range(num_slots - 1, -1, -1):
                slot = obj.material_slots[i]
                self.remove_mat(slot, material, materials)
                        
        return {'FINISHED'}
    
    def remove_mat(self, slot, material,  materials):
        if slot.material == material:
            # Get the material slot index
            
            if self.delete_slot:
                # Remove the material slot from the object
                obj_mats.pop(index=i)
            else:
                slot.material = None
               
    
class EASEtool_OT_Delete_Unused_Slots(Operator):
    """Delete unused slots from selection or all"""
    bl_idname = "easetool.delete_unused_slots"
    bl_label = "Delete Unused Slots"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'OBJECT'
    
    selected_only: BoolProperty( name = "Only From Selected", default = False)
    keep_original: BoolProperty( name = "Keep Original Selection", description = "Keep original selection after removing material slots from all", default = True)
    
    def execute(self, context):
       
        objects = get_objects(self.selected_only)
        
        if not self.selected_only:
            sel = get_objects(True)
            
            ## select all i objects 
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects:
                obj.select_set(True)
                
            bpy.ops.object.material_slot_remove_unused()
            
            if self.keep_original:
                ## Select the original selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in sel:
                    obj.select_set(True)
        else:
            bpy.ops.object.material_slot_remove_unused()
        
                    
        return {'FINISHED'}
    
    
class EASEtool_OT_Add_Material(Operator):
    """Delete unused slots from selection or all"""
    bl_idname = "easetool.add_material"
    bl_label = "Add material to selection or all"
    
    @classmethod
    def poll(cls, context):
        # Check if there are any materials in the blend file
        return any_materials()
    
    index: IntProperty( name = "Index", default = -1 )   
    selected_only: BoolProperty( name = "Only From Selected", default = True)
    overwrite: BoolProperty( name = "Overwrite origianl materials", default = False)
    to_end: BoolProperty( name = "Add the material to the end of the list", default = False)
    
    def execute(self, context):
        objects = get_objects(self.selected_only)
        
        ## Check if mateiral index is given
        index = self.index
        
        material = bpy.data.materials[index]
        
        ## Add material
        for obj in objects:
            obj_mats = obj.data.materials
            if self.overwrite:
                obj_mats.clear()
            ## Check if material is already applied to object and break loop if so
            elif any(mat == material for mat in obj_mats): 
                    break
                                
            obj_mats.append(material)
            
            if not self.to_end:
                ## Move the new slot to the front
                for i in range(len(obj_mats) - 1, 0, -1):
                    obj_mats[i] = obj_mats[i - 1]

                ## Assign the material to the first slot
                obj.data.materials[0] = material
                
                    
        return {'FINISHED'}


class EASEtool_OT_Assign_Fake_User(Operator):
    """Assign or remove fake user from material"""
    bl_idname = "easetool.asign_fake_user"
    bl_label = "Assign Fake User"    
    
    @classmethod
    def poll(cls, context):
        # Check if there are any materials in the blend file
        return any_materials()
    
    remove: BoolProperty( name = "Remove Fake User", default = False)
    
    def execute(self, context):
                
        index = context.scene.ease_mat_prop_grp.material_index
        material = bpy.data.materials[index]
        
        material.use_fake_user = not self.remove
        
        return {'FINISHED'}    
    
    

class EASEtool_OT_Create_Material(Operator):
    """Create a material with selected shader"""
    bl_idname = "easetool.create_material"
    bl_label = "Add material to selection or all"    
    
    random_color: BoolProperty( name = "Random Color", default = False)
    name: StringProperty( name = "Material Name", default = "Material")
    color: FloatVectorProperty(
        name = "Color", subtype = 'COLOR',
        size = 4, default = (1.0, 1.0, 1.0, 1.0),
        min = 0.0, max = 1.0)
    type: StringProperty( name = "Shader Type", default = 'ShaderNodeBsdfPrincipled')
    
    def execute(self, context):
        material = bpy.data.materials.new(name=self.name)
        
        if self.random_color:
            self.color = self.make_random_color()
        
        material.use_nodes = True
        tree = material.node_tree
        nodes = tree.nodes
        
        nodes.clear()
        ## Add Shader
        shader = nodes.new(self.type)
        shader.inputs[0].default_value = self.color
        ## Add Output
        output = nodes.new("ShaderNodeOutputMaterial")
        ## Connect nodes
        tree.links.new(shader.outputs[0], output.inputs[0])

        material.diffuse_color = self.color
                    
        return {'FINISHED'}
    
    def make_random_color(self) -> ():
        h = random()  # Random hue between 0 and 1
        s = 0.8  
        v = 1.0
        a = 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
                
        return (r,g,b,a)

class EASEtool_OT_Create_Face_Strength_Material(Operator):
    """Create a face strength indicator material"""
    bl_idname = "easetool.create_face_strength_material"
    bl_label = "Create a Material To Show Face Strength"
        
    name: StringProperty( name = "New material Name", default = "[FACE STRENGTH INDICATOR]")
        
    def execute(self, context):
        
        ## Check if material already exists
        materials = bpy.data.materials
        if self.name in materials:
            return {'FINISHED'}
        
        ## Create new material
        material = bpy.data.materials.new(name=self.name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
#        tree = material.node_tree
#        nodes = tree.nodes
        
        nodes.clear()
        material.diffuse_color = (1,0,0.5,1)
        
        ## Create new nodes
        attribute_node = nodes.new('ShaderNodeAttribute')
        attribute_node.attribute_name  = '__mod_weightednormals_faceweight'
        attribute_node.location = (0, 0)

        math_node = nodes.new('ShaderNodeMath')
        math_node.operation = 'ADD'
        math_node.location = (200, 0)

        ramp_node = nodes.new('ShaderNodeValToRGB')
        ramp_node.color_ramp.interpolation = 'CONSTANT'
        ramp_node.color_ramp.elements[0].position = 0
        ramp_node.color_ramp.elements[0].color = (0.1, 0.136, 1, 1)
        ramp_node.color_ramp.elements[1].position = 0.33
        ramp_node.color_ramp.elements[1].color = (0.118, 1, 0.1, 1)
        ramp_node.color_ramp.elements.new(0.66)
        ramp_node.color_ramp.elements[2].color = (1, 0.1, 0.1, 1)
        ramp_node.location = (400, 0)

        emission_node = nodes.new('ShaderNodeEmission')
        emission_node.inputs[0].default_value = (1,0,0.5,1)
        emission_node.location = (700, 0)

        output_node = nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (900, 0)

        # Link the nodes
        links = material.node_tree.links
        links.new(attribute_node.outputs['Fac'], math_node.inputs[0])
        links.new(math_node.outputs['Value'], ramp_node.inputs['Fac'])
        links.new(ramp_node.outputs['Color'], emission_node.inputs['Color'])
        links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
             
        return {'FINISHED'}
    
    
#class EASEtool_OT_Create_Ngon_Material(Operator):
#    """Create and asign materials based on nr of vertices per face and add to selected objects"""
#    bl_idname = "easetool.create_ngon_material"
#    bl_label = "Create a Materials To Show Ngons, Quads and Tris"
#    
#    @classmethod
#    def poll(cls, context):
#        # Check if there are any materials in the blend file
#        return bpy.context.object.type == 'MESH'
#        
#    ngon_name: StringProperty( name = "Ngon material Name", default = "[NGON INDICATOR]")
#    quad_name: StringProperty( name = "Quad material Name", default = "[QUAD INDICATOR]")
#    tris_name: StringProperty( name = "Tris material Name", default = "[TRIS INDICATOR]")
#    
#    def execute(self, context):
#        mesh = obj.data

#        ## Check if materials already exists
#        materials = bpy.data.materials
#        ## Check if material exists in object
#
#        quads = []
#        ngons = []
#        tris = []
#        
#        ## Get ngons quads tris
#        for polygon in mesh.polygons:
#            if len(polygon.vertices) == 4:
#                quads.append(polygon)
#            elif len(polygon.vertices) < 4:
#                tris.append(polygon)
#            elif len(polygon.vertices) > 4:
#                ngons.append(polygon)
#        
#        ## Assign

#        return {'FINISHED'}


class EASEtool_OT_Colorize_Materials(Operator):
    """Set Material Diffuse color to shader default color"""
    bl_idname = "easetool.colorize"
    bl_label = "Colorize Materials"
    bl_icon = "MATERIAL"
    
    @classmethod
    def poll(cls, context):
        ## Check if there are any materials in the blend file
        return any_materials()
    
    def execute(self, context):
        materials = bpy.data.materials
        
        for m in materials:

            ## Get the material output node
            material_output = m.node_tree.nodes.get('Material Output')

            ## if material output doesn't exist ignore
            if not material_output:
                continue           
        
            ## Get the input shader of the material output node
            input_shader = material_output.inputs['Surface'].links[0].from_node
            
            ## Check if the input shader exists
            if not input_shader:
                continue
            
            color = ()
            ## Check if the node is Add or Mix nodes
            if input_shader.type == 'ShaderNodeMixShader':
                color = (0.583, 0.922, 0.227, 1)
            elif input_shader.type == 'ShaderNodeAddShader':
                color = (0.333, 0.814, 0.130, 1)
            else: 
                ## Get the color from the input shader
                ## Most if not all Shaders have color node at index 0
                color = input_shader.inputs[0].default_value
            
            m.diffuse_color = color



        return {'FINISHED'}




#############################################################
####    UI    ###############################################
#############################################################

class EASEtool_PT_Material_Panel(Panel):
    """Material Edit Panel"""
    bl_label = "EASEtool: Materials"
    bl_idname = "EASETOOL_MT_material_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Materials'
        

    def draw(self, context):
        scene = context.scene;
        data = bpy.data
        materials = data.materials
        
        ## UI Props
        props = scene.ease_mat_prop_grp
        index = props.material_index
        
        layout = self.layout
        col = layout.column(align=True)
        
        
        ## Material List
        list = col.template_list("EASEtool_UL_Material_List", "Material List", data, "materials", props, "material_index")
               
        if len(materials) > 0:
            active_material = materials[index]   
            
        ## Create Material
        box = col.box()
        c = box.column()
        
        
        op = c.operator("easetool.create_material", text="Create New Material", icon="NODE_MATERIAL")
        op.name = props.new_name
        op.color = props.new_color
        op.random_color = props.random_color
        op.type = props.new_shader
        
        ## Get Name
        row = c.split(factor=0.2, align=True)
        row.label(text="Name:")
        row.prop(props, "new_name", text="")
        row = c.split(factor=0.2, align=True)
        ## Get Color
        row.label(text="Color:")
        row = row.row( translate = False)
        c1 = row.column()
        c1.active = not props.random_color
        c1.prop(props, "new_color", text="")
        row.prop(props, "random_color", text="")
        row = c.split(factor=0.2, align=True)
        ## Get Shader
        row.label(text="Shader:")
        row.prop(props, "new_shader", text="")
        
        
        ## Colorize Materials
        col.separator()
        box = col.box()
        box.operator("easetool.colorize")
        
                
        ## Object Section
        col.separator()
        box = col.box()
        
        box.label(text="Object")
        c = box.column(align=True)

        ## Add Material to objects 
        ## set parameters for the add buttons
        def set_params(operator: Operator):            
            operator.overwrite = props.overwrite_original
            operator.to_end = props.to_end
        
            
        op = c.operator("easetool.add_material", text="Add Material to Selection")
        op.index = index
        op.selected_only = True
        set_params(op)
        op = c.operator("easetool.add_material", text="Add Material to All")
        op.selected_only = False
        set_params(op)
       
        
        row = c.row(align=True)
        row.active = any_materials()
        c1 = row.column()
        c1.prop(props, "overwrite_original", text="Remove Old")
        
        c2 = row.column()
        c2.active = not props.overwrite_original
        c2.prop(props, "to_end", text="Add To Last Slot")
        
        ## Remove Material From object
        c.separator()
        op = c.operator("easetool.remove_material", text="Remove Material From Selected")
        op.index = index
        op.selected_only = True
        op.delete_slot = props.delete_slot
        c.operator("easetool.remove_material", text="Remove Material From All")
        op.selected_only = False
        op.delete_slot = props.delete_slot

        row = c.row()
        row.active = len(materials) > 0
        row.prop(props, "delete_slot")
        
        ## Material Slots
        c.separator()
        c.operator("easetool.delete_unused_slots", text="Delete Unused Slots From Selected").selected_only = True
        
        row = c.row(align=True, translate=False)
        row.active = context.mode == 'OBJECT'
        op = row.operator("easetool.delete_unused_slots", text="Delete All Unused Slots")
        op.selected_only = False
        op.keep_original = props.keep_original
        row.prop(props, "keep_original", text = "", icon = "RESTRICT_SELECT_OFF")
                
        ## Remove Material from File
        col.separator()
        box = col.box()
        box.label(text="File")
        c = box.column(align=True)
        
        op = c.operator("easetool.delete_materials", text="Delete Selected Material", icon="FILE_BACKUP")
        op.index = index
        op.delete_all = False ## Crahses sometimes Index issue
        c.operator("easetool.delete_unused_materials", text="Delete All Orphan Materials", icon="ORPHAN_DATA")
        c.operator("easetool.delete_materials", text="Delete All Materials", icon="TRASH").delete_all = True 
        
                
        ## Material Presets
        col.separator()
        box = col.box()
        box.label(text="Presets")
        c = box.column(align=True)
        
        c.operator("easetool.create_face_strength_material", text="Face Strength indicator Material", icon="MOD_NORMALEDIT")
        

#############################################################
####    REGISTRATION    #####################################
#############################################################

classes = [ EASEtool_UL_Material_List, EASEtool_PT_Material_Panel, EASEtool_Material_Property_Group,
            EASEtool_OT_Delete_Materials, EASEtool_OT_Delete_Unused_Materials, EASEtool_OT_Remove_Material,
            EASEtool_OT_Delete_Unused_Slots, EASEtool_OT_Add_Material, EASEtool_OT_Assign_Fake_User, 
            EASEtool_OT_Create_Material, EASEtool_OT_Create_Face_Strength_Material, EASEtool_OT_Colorize_Materials
            ]

from bpy.utils import register_class, unregister_class

def register():
    for c in classes:
        register_class(c)
        
    bpy.types.Scene.ease_mat_prop_grp = PointerProperty(type=EASEtool_Material_Property_Group)

def unregister():
    for c in classes:
        unregister_class(c)
        
    del bpy.types.Scene.ease_mat_prop_grp

if __name__ == "__main__":
    register()

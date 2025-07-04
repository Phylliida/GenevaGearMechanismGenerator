# -------------------------------------------------------------
#  Geneva Mechanism Generator
# -------------------------------------------------------------
bl_info = {
    "name":        "Geneva Mechanism",
    "author":      "TessaCoil - help from o3",
    "version":     (1, 0, 0),
    "blender":     (3, 0, 0),
    "location":    "Add > Mesh",
    "description": "Generates a Geneva Mechanism with Adjustable Parameters",
    "category":    "Add Mesh",
}

import bpy, math, textwrap, re



# ----------------------------------------------------------------
#  Operator — supplies parameters and runs the script
# ----------------------------------------------------------------
class MESH_OT_geneva_wrapper(bpy.types.Operator):
    bl_idname  = "mesh.geneva_mechanism"
    bl_label   = "Geneva Mechanism"
    bl_options = {'REGISTER', 'UNDO'}

    # parameters (defaults are the same as in the original code)
    genevaHeight              : bpy.props.FloatProperty(default=0.4,  name="Height")
    genevaWheelRadius         : bpy.props.FloatProperty(default=3.0,  name="Wheel Radius")
    genevaWheelSlotQuantity   : bpy.props.IntProperty  (default=6,    name="Wheel Slot Quantity", min=3)
    genevaCrankPinRadius    : bpy.props.FloatProperty(default=0.125, name="Crank-Pin Radius")
    allowedClearance          : bpy.props.FloatProperty(default=0.05, name="Slot Clearance")
    pinTolerence              : bpy.props.FloatProperty(default=0.05, name="Pin Tol.")
    stopDiscTolerence         : bpy.props.FloatProperty(default=0.05, name="Stop-Disc Tol.")
    stopDiscCutoutTolerence   : bpy.props.FloatProperty(default=0.05, name="Stop-Cutout Tol.")
    baseTolerence             : bpy.props.FloatProperty(default=0.05, name="Base Tol.")
    wheelHoleSize             : bpy.props.FloatProperty(default=0.25, name="Wheel Hole Radius")
    crankHoleSize             : bpy.props.FloatProperty(default=0.25, name="Crank Hole Radius")
    holeTolerence             : bpy.props.FloatProperty(default=0.05, name="Hole Tol.")
    vertices                  : bpy.props.IntProperty  (default=128,  name="Cylinder Verts", min=3, max=512)


    # ------------------------------------------------------------
    def execute(self, context):
        
        prev_names = context.scene.get("geneva_objects", [])
        for name in prev_names:
            obj = bpy.data.objects.get(name)
            if obj:                                # may already have been deleted
                bpy.data.objects.remove(obj, do_unlink=True)
         
        before = set(bpy.data.objects)
        import math
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        genevaHeight = self.genevaHeight
        genevaWheelRadius = self.genevaWheelRadius
        genevaWheelSlotQuantity = self.genevaWheelSlotQuantity
        genevaCrankPinRadius = self.genevaCrankPinRadius
        allowedClearance = self.allowedClearance
        pinTolerence = self.pinTolerence
        stopDiscTolerence = self.stopDiscTolerence
        stopDiscCutoutTolerence = self.stopDiscCutoutTolerence
        baseTolerence = self.baseTolerence
        wheelHoleSize = self.wheelHoleSize
        crankHoleSize = self.crankHoleSize
        holeTolerence = self.holeTolerence
        vertices = self.vertices
        
        genevaCrankPinDiameter = genevaCrankPinRadius*2
        centerDistance = genevaWheelRadius/math.cos(math.pi/genevaWheelSlotQuantity)
        genevaCrankRadius = math.sqrt(centerDistance**2-genevaWheelRadius**2)
        slotCenterLength = (genevaCrankRadius + genevaWheelRadius) - centerDistance
        slotWidth = genevaCrankPinDiameter + allowedClearance
        stopArcRadius = genevaCrankRadius - (genevaCrankPinDiameter*1.5)
        stopDiscRadius = stopArcRadius - allowedClearance
        clearanceArc = genevaWheelRadius * stopDiscRadius / genevaCrankRadius

        def selectItem(name):
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[name].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[name] 
        
        def applyBooleanOperator(targetName, otherName, operatorName, solver):
            selectItem(targetName)
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.context.object.modifiers["Boolean"].operation = operatorName
            bpy.context.object.modifiers["Boolean"].solver = solver
            bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[otherName]
            bpy.ops.object.modifier_apply(modifier="Boolean")

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=genevaWheelRadius, depth=genevaHeight/2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        rootBoiName = bpy.context.active_object.name
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=stopDiscRadius, depth=genevaHeight, enter_editmode=False, align='WORLD', location=(centerDistance, 0, 0), scale=(1, 1, 1))
        beeHelperName = bpy.context.active_object.name

        rotateAmount = 2*math.pi/genevaWheelSlotQuantity
        for i in range(genevaWheelSlotQuantity):
            applyBooleanOperator(rootBoiName, beeHelperName, "DIFFERENCE", "FAST")
            bpy.ops.transform.rotate(value=rotateAmount, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
            

        bpy.ops.transform.rotate(value=rotateAmount/2, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
        slotPos = centerDistance - genevaCrankRadius
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=genevaCrankPinDiameter/2, depth=genevaHeight, enter_editmode=False, align='WORLD', location=(slotPos, 0, 0), scale=(1, 1, 1))
        littlePokyName = bpy.context.active_object.name
        bpy.ops.mesh.primitive_cube_add(size=genevaCrankPinDiameter, enter_editmode=False, align='WORLD', location=(slotPos+centerDistance, 0, 0), scale=(1, 1, 1))
        helperLongCubeName = bpy.context.active_object.name
        bpy.ops.transform.resize(value=(centerDistance/genevaCrankPinDiameter*2, 1, genevaHeight/genevaCrankPinDiameter), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
        
        applyBooleanOperator(littlePokyName, helperLongCubeName, "UNION", "EXACT")

        for i in range(genevaWheelSlotQuantity+1):
            applyBooleanOperator(rootBoiName, littlePokyName, "DIFFERENCE", "EXACT")
            bpy.ops.transform.rotate(value=rotateAmount, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

        selectItem(helperLongCubeName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        selectItem(littlePokyName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        selectItem(beeHelperName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=genevaCrankPinDiameter/2-pinTolerence, depth=genevaHeight/2, enter_editmode=False, align='WORLD', location=(slotPos, 0, 0), scale=(1, 1, 1))
        littlePokyName = bpy.context.active_object.name

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=stopDiscRadius-stopDiscTolerence, depth=genevaHeight/2, enter_editmode=False, align='WORLD', location=(centerDistance, 0, 0), scale=(1, 1, 1))
        beeHelperName = bpy.context.active_object.name

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=genevaWheelRadius+stopDiscCutoutTolerence, depth=genevaHeight, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        stopDiscCutoutName = bpy.context.active_object.name

        applyBooleanOperator(beeHelperName, stopDiscCutoutName, "DIFFERENCE", "EXACT")

        selectItem(stopDiscCutoutName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        slottyBoiBaseRadius = centerDistance-slotPos+genevaCrankPinDiameter/2-pinTolerence

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=slottyBoiBaseRadius, depth=genevaHeight/2, enter_editmode=False, align='WORLD', location=(centerDistance, 0, -genevaHeight/2), scale=(1, 1, 1))
        slottyBoiBaseName = bpy.context.active_object.name

        spokyBoiBaseRadius = centerDistance-slottyBoiBaseRadius-baseTolerence
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=spokyBoiBaseRadius, depth=genevaHeight/2, enter_editmode=False, align='WORLD', location=(0, 0, -genevaHeight/2), scale=(1, 1, 1))
        spokyBoiBaseName = bpy.context.active_object.name

        applyBooleanOperator(rootBoiName, spokyBoiBaseName, "UNION", "EXACT")
        selectItem(spokyBoiBaseName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=wheelHoleSize, depth=genevaHeight*2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        wheelCutoutName = bpy.context.active_object.name
        applyBooleanOperator(rootBoiName, wheelCutoutName, "DIFFERENCE", "EXACT")

        selectItem(wheelCutoutName)
        bpy.ops.object.delete(use_global=False, confirm=False)






        applyBooleanOperator(slottyBoiBaseName, littlePokyName, "UNION", "EXACT")

        selectItem(littlePokyName)
        bpy.ops.object.delete(use_global=False, confirm=False)

        applyBooleanOperator(slottyBoiBaseName, beeHelperName, "UNION", "EXACT")

        selectItem(beeHelperName)
        bpy.ops.object.delete(use_global=False, confirm=False)



        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=crankHoleSize, depth=genevaHeight*2, enter_editmode=False, align='WORLD', location=(centerDistance, 0, 0), scale=(1, 1, 1))
        crankCutoutName = bpy.context.active_object.name

        applyBooleanOperator(slottyBoiBaseName, crankCutoutName, "DIFFERENCE", "EXACT")

        selectItem(crankCutoutName)
        bpy.ops.object.delete(use_global=False, confirm=False)



        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=crankHoleSize-holeTolerence, depth=genevaHeight*2, enter_editmode=False, align='WORLD', location=(centerDistance, 0, -genevaHeight/2+genevaHeight/4), scale=(1, 1, 1))
        crankCutoutName = bpy.context.active_object.name

        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=wheelHoleSize-holeTolerence, depth=genevaHeight*2, enter_editmode=False, align='WORLD', location=(0, 0, -genevaHeight/2+genevaHeight/4), scale=(1, 1, 1))
        wheelCutoutName = bpy.context.active_object.name


        after      = set(bpy.data.objects)
        new_objs   = [obj.name for obj in (after - before)]
        # --------------------------------------------------------
        # 4)  Store the new list on the scene so we can delete them
        #     next time the operator is called.
        # --------------------------------------------------------
        context.scene["geneva_objects"] = new_objs

        return {'FINISHED'}


# ----------------------------------------------------------------
#  Simple sidebar panel
# ----------------------------------------------------------------
class VIEW3D_PT_geneva(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category   = "Geneva"
    bl_label      = "Geneva Mechanism"

    def draw(self, context):
        self.layout.operator(MESH_OT_geneva_wrapper.bl_idname, text="Create Geneva")


# ----------------------------------------------------------------
#  Add-menu entry
# ----------------------------------------------------------------
def menu_func(self, ctx):
    self.layout.operator(MESH_OT_geneva_wrapper.bl_idname, icon='MESH_CYLINDER')


# ----------------------------------------------------------------
#  Registration
# ----------------------------------------------------------------
classes = (MESH_OT_geneva_wrapper, VIEW3D_PT_geneva)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
import Autodesk

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Retrieve element from selection set
sel = uidoc.Selection
set = sel.GetElementIds()

if len(set) == 0:
    message =("Revit", "Please select at least one element.")
else:
    # Iterate through selected elements
    for elementId in set:
        element = doc.GetElement(elementId)
        location_curve = element.Location.Curve
        line = location_curve.Clone()
        p = line.GetEndPoint(0)
        q = line.GetEndPoint(1)
        start_point = line.GetEndPoint(0)
        end_point = line.GetEndPoint(1)
        v = end_point - start_point

    # Modify section box to fit element bounding box
bb = element.get_BoundingBox(None)
if bb is None:
    message = "Could not retrieve bounding box of element."
else:
    if not isinstance(bb, BoundingBoxXYZ):
        message = "Retrieved object is not a bounding box."
    else:
        minz = bb.Min.Z
        maxz = bb.Max.Z
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        
        minZ = float('inf')
        maxZ = -float('inf')
        
        for level in levels:
            elev = level.Elevation
        if elev < minZ:
            minZ = elev
        if elev > maxZ:
            maxZ = elev

# Add some padding to the section box height
        padding = 1 #10
        minZ -= padding
        maxZ += padding

        if minZ >= 0:
            minZ = -padding
        #w = 1


            # Add some padding to the section box dimensions
           
            # Create section box
        w = 8
        offset = 0.1 * w
        min = XYZ(-w, minZ - offset, -offset)
        max = XYZ(w, maxZ + offset, 0)
        midpoint = p + 0.1 * v
        traydir = v.Normalize()
        DB= Autodesk.Revit.DB
        up = DB.XYZ.BasisZ
        viewdir = traydir.CrossProduct(up)
        t = Transform.Identity
        t.Origin = midpoint
        t.BasisX = traydir
        t.BasisY = up
        t.BasisZ = viewdir
        sectionBox = BoundingBoxXYZ()
        sectionBox.Transform = t
        sectionBox.Min = XYZ(min.X, min.Y, minZ)
        sectionBox.Max = XYZ(max.X, max.Y, maxZ)

            # Create section view
        view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
        view_type = None
        for view_family_type in view_family_types:
            if view_family_type.ViewFamily == ViewFamily.Section:
                view_type = view_family_type
                break

        if view_type is None:
            message = "Could not find a section view type."
        else:
            vft = view_type
            views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()

        with Transaction(doc) as tx:
            tx.Start("Create Section View")
            section_view = ViewSection.CreateSection(doc, vft.Id, sectionBox)
            for view in views:
                if hasattr(view, 'IsSectionBoxVisible') and hasattr(view, 'IsSectionLineVisible'):
                    if view.ViewFamily == ViewFamily.Section:
                        view.IsSectionBoxVisible = True
                        view.IsSectionLineVisible = True

             
            tx.Commit()
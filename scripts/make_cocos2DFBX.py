# python

import os
import shlex
import sys
import FbxCommon
import time
import cPickle
from fbx import *

def error(text):
    print(str(text))
    raw_input("Press any key to continue...")
    sys.exit(1)

def element_count(p):
  q = p[:]
  count = 0
  while q:
    entry = q.pop()
    if isinstance(entry, list) or isinstance(entry, tuple):
      q += entry
    count += 1
  return count

def CreateTexture(pSdkManager, pMesh, material_name, texture_name, texture_path,uv):
    # A texture need to be connected to a property on the material,
    # so let's use the material (if it exists) or create a new one
    lMaterial = None

    # get the node of mesh, add material for it.
    lNode = pMesh.GetNode()
    lMaterialName = material_name
    lShadingName  = "Phong"
    lBlack = FbxDouble3(0.0, 0.0, 0.0)
    lRed = FbxDouble3(1.0, 0.0, 0.0)
    lDiffuseColor = FbxDouble3(0.75, 0.75, 0.0)
    lMaterial = FbxSurfacePhong.Create(pSdkManager, lMaterialName)

    lMaterial.Emissive.Set(lBlack)
    lMaterial.Ambient.Set(lRed)
    lMaterial.AmbientFactor.Set(1.)
    lMaterial.Diffuse.Set(lDiffuseColor)
    lMaterial.DiffuseFactor.Set(1.)
    lMaterial.TransparencyFactor.Set(0.4)
    lMaterial.ShadingModel.Set(lShadingName)
    lMaterial.Shininess.Set(0.5)
    lMaterial.Specular.Set(lBlack)
    lMaterial.SpecularFactor.Set(0.3)

    lNode.AddMaterial(lMaterial)
    
    lTexture = FbxFileTexture.Create(pSdkManager,texture_name)
    lTexture.SetFileName(texture_path) 
    lTexture.SetTextureUse(FbxTexture.eStandard)
    lTexture.SetMappingType(FbxTexture.eUV)
    lTexture.SetMaterialUse(FbxFileTexture.eModelMaterial)
    lTexture.SetSwapUV(False)
    lTexture.SetTranslation(0.0, 0.0)
    lTexture.SetScale(1.0, 1.0)
    lTexture.SetRotation(0.0, 0.0)

    if lMaterial:
        lMaterial.Diffuse.ConnectSrcObject(lTexture)
        lTexture.UVSet.Set(uv)

filename = sys.argv[1]
if not filename:
    error("Output file not set")

fbx_file = open(filename, 'r')
data = cPickle.load(fbx_file)
fbx_file.close()
os.remove(filename)

# Prepare the FBX SDK.
(lSdkManager, lScene) = FbxCommon.InitializeSdkObjects()

# Create the scene.
lMesh = FbxMesh.Create(lSdkManager,data['name'])
verts = list()
normals = list()
uvs = list()
num_polys = len(data['polys'])

for vert in data['verts']:
    verts.append(FbxVector4(vert[0],vert[1],vert[2]))
for normal in data['normals']:
    normals.append(FbxVector4(normal[0],normal[1],normal[2]))

count = 0
lMesh.InitControlPoints(len(verts))
for vert in verts:
    lMesh.SetControlPointAt(vert, count)
    count+=1
        
lLayer = lMesh.GetLayer(0)
if lLayer == None:
    lMesh.CreateLayer()
    lLayer = lMesh.GetLayer(0)
        
lLayerElementNormal= FbxLayerElementNormal.Create(lMesh, "Normals")
lLayerElementNormal.SetMappingMode(FbxLayerElement.eByControlPoint)
lLayerElementNormal.SetReferenceMode(FbxLayerElement.eDirect)

for normal in normals:
    lLayerElementNormal.GetDirectArray().Add(normal)

lLayer.SetNormals(lLayerElementNormal)

poly_count = 0

for poly in data['polys']:
    lMesh.BeginPolygon(-1, -1, False)
    for vert in poly:
        lMesh.AddPolygon(vert)
    poly_count+=1
    lMesh.EndPolygon()
    
    
lNode = FbxNode.Create(lSdkManager,data['name'])
lNode.SetNodeAttribute(lMesh)
lNode.SetShadingMode(FbxNode.eTextureShading)

count = 0
for material in data['materials']:
    lLayer = lMesh.GetLayer(count)
    if lLayer == None:
        lMesh.CreateLayer()
        lLayer = lMesh.GetLayer(count)
    lMaterialLayer=FbxLayerElementMaterial.Create(lMesh, material)
    lMaterialLayer.SetMappingMode(FbxLayerElement.eByPolygon)
    lMaterialLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
    lLayer.SetMaterials(lMaterialLayer)
    poly_count = 0
    lMaterialLayer.GetIndexArray().SetCount(num_polys)
    for poly_material in data['polymaterials']:
        if material == poly_material:
            lMaterialLayer.GetIndexArray().SetAt(poly_count,count)
        else:
            lMaterialLayer.GetIndexArray().SetAt(poly_count,-1)
        poly_count += 1
    for mat_texture in data['textures']:
        if mat_texture in data['materials'][material]:
            clip = data['textures'][mat_texture]
            CreateTexture(lSdkManager, lMesh, material, mat_texture, clip[0], clip[1])
            break
    count += 1
    
count = 0    
for uvmap in data['uvmaps']:
    lLayer = lMesh.GetLayer(count)
    if lLayer == None:
        lMesh.CreateLayer()
        lLayer = lMesh.GetLayer(count)
    lUVDiffuseLayer = FbxLayerElementUV.Create(lMesh, uvmap[0])
    lUVDiffuseLayer.SetMappingMode(FbxLayerElement.eByPolygonVertex)
    lUVDiffuseLayer.SetReferenceMode(FbxLayerElement.eDirect)
    lLayer.SetUVs(lUVDiffuseLayer, FbxLayerElement.eTextureDiffuse)
    for uv in uvmap[1]:
        for i in xrange(0, len(uv), 2):
            lUVDiffuseLayer.GetDirectArray().Add(FbxVector2(uv[i], uv[i+1]))
    count += 1

count = 0    
for colormap in data['colormaps']:
    lLayer = lMesh.GetLayer(count)
    if lLayer == None:
        idx = lMesh.CreateLayer()
        lLayer = lMesh.GetLayer(count)
    lVertexColorLayer = FbxLayerElementVertexColor.Create(lMesh, colormap[0])
    lVertexColorLayer.SetMappingMode(FbxLayerElement.eByControlPoint)
    lVertexColorLayer.SetReferenceMode(FbxLayerElement.eDirect)
    lLayer.SetVertexColors(lVertexColorLayer)
    for color in colormap[1]:
        lVertexColorLayer.GetDirectArray().Add(FbxColor(color[0], color[1], color[2]))
    count += 1

#lResult = CreateScene(lSdkManager, lScene, filename)


lRootNode = lScene.GetRootNode()
lRootNode.AddChild(lNode)

lResult = FbxCommon.SaveScene(lSdkManager, lScene, filename)

if lResult == False:
    print("\n\nAn error occurred while saving the scene...\n")
    lSdkManager.Destroy()
    sys.exit(1)

# Destroy all objects created by the FBX SDK.
lSdkManager.Destroy()

sys.exit(0)


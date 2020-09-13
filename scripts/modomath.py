import math
import operator
from math import asin, atan, atan2
from itertools import izip
import lx

verbose = False

def vecAdd(vec1, vec2):
    return tuple(x + y for x, y in izip(vec1, vec2)) 

def vecDistance(vec1, vec2):
    return vecNorm(vecSub(vec1, vec2))

def vecSub(vec1, vec2):
    return tuple(x - y for x, y in izip(vec1, vec2))

def vecNorm(vec):
    return vecDotProduct(vec, vec) ** 0.5

def vecScalarMul(vec,scalar):
    return tuple(x * scalar for x in vec)

def vecDotProduct(vec1, vec2):
    return sum(x1 * x2 for x1, x2 in izip(vec1, vec2))

def vecDistanceAxis(axis, vec):
    return vecNorm(vecNormal(axis[0], axis[1], vec)) / vecDistance(*axis)

def vecNormal(vec1, vec2, vec3):
    return vecCrossProduct(vecSub(vec2, vec1), vecSub(vec3, vec1))

def vecNormalized(vec):
    try:
        return vecScalarMul(vec, 1.0 / vecNorm(vec))
    except ZeroDivisionError:
        return 0
    
def vecCrossProduct(vec1, vec2):
    return (vec1[1] * vec2[2] - vec1[2] * vec2[1],
            vec1[2] * vec2[0] - vec1[0] * vec2[2],
            vec1[0] * vec2[1] - vec1[1] * vec2[0])

def vecDistanceTriangle(triangle, vert):
    normal = vecNormal(*triangle)
    return vecDotProduct(normal, vecSub(vert, triangle[0])) \
           / vecNorm(normal)

def vecAngle(vec1, vec2):
    try:
        return math.acos(round(vecDotProduct(vecNormalized(vec1),vecNormalized(vec2)),13))
    except:
        return math.acos(1)

def basesimplex3d(vertices, precision):
    """Find four extreme points, to be used as a starting base for the
    quick hull algorithm L{qhull3d}.

    The algorithm tries to find four points that are
    as far apart as possible, because that speeds up the quick hull
    algorithm. The vertices are ordered so their signed volume is positive.

    If the volume zero up to C{precision} then only three vertices are
    returned. If the vertices are colinear up to C{precision} then only two
    vertices are returned. Finally, if the vertices are equal up to C{precision}
    then just one vertex is returned.

    >>> import random
    >>> cube = [(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)]
    >>> for i in range(200):
    ...     cube.append((random.random(), random.random(), random.random()))
    >>> base = basesimplex3d(cube)
    >>> len(base)
    4
    >>> (0,0,0) in base
    True
    >>> (1,1,1) in base
    True

    :param vertices: The vertices to construct extreme points from.
    :param precision: Distance used to decide whether points coincide,
        are colinear, or coplanar.
    :return: A list of one, two, three, or four vertices, depending on the
        the configuration of the vertices.
    """
    # sort axes by their extent in vertices
    extents = sorted(range(3),
                     key=lambda i:
                     max(vert[i] for vert in vertices)
                     - min(vert[i] for vert in vertices))
    # extents[0] has the index with largest extent etc.
    # so let us minimize and maximize vertices with key
    # (vert[extents[0]], vert[extents[1]], vert[extents[2]])
    # which we can write as operator.itemgetter(*extents)(vert)
    vert0 = min(vertices, key=operator.itemgetter(*extents))
    vert1 = max(vertices, key=operator.itemgetter(*extents))
    # check if all vertices coincide
    #if vecDistance(vert0, vert1) < precision:
    #    return [ vert0 ]
    # as a third extreme point select that one which maximizes the distance
    # from the vert0 - vert1 axis
    vert2 = max(vertices,
                key=lambda vert: vecDistanceAxis((vert0, vert1), vert))
    #check if all vertices are colinear
    if vecDistanceAxis((vert0, vert1), vert2) < precision:
        return [ vert0, vert1 ]
    # as a fourth extreme point select one which maximizes the distance from
    # the v0, v1, v2 triangle
    vert3 = max(vertices,
                key=lambda vert: abs(vecDistanceTriangle((vert0, vert1, vert2),
                                                         vert)))
    # ensure positive orientation and check if all vertices are coplanar
    orientation = vecDistanceTriangle((vert0, vert1, vert2), vert3)
    if orientation > precision:
        return [ vert0, vert1, vert2, vert3 ]
    elif orientation < -precision:
        return [ vert1, vert0, vert2, vert3 ]
    else:
        # coplanar
        return [ vert0, vert1, vert2 ]

def qhull3d(vertices, precision):
    """Return the triangles making up the convex hull of C{vertices}.
    Considers distances less than C{precision} to be zero (useful to simplify
    the hull of a complex mesh, at the expense of exactness of the hull).

    :param vertices: The vertices to find the hull of.
    :param precision: Distance used to decide whether points lie outside of
        the hull or not. Larger numbers mean fewer triangles, but some vertices
        may then end up outside the hull, at a distance of no more than
        C{precision}.
    :param verbose: Print information about what the algorithm is doing. Only
        useful for debugging.
    :return: A list cointaining the extreme points of C{vertices}, and
        a list of triangle indices containing the triangles that connect
        all extreme points.
    """
    # find a simplex to start from
    hull_vertices = basesimplex3d(vertices, precision)

    # handle degenerate cases
    if len(hull_vertices) == 3:
        # coplanar
        hull_vertices = qhull2d(vertices, vecNormal(*hull_vertices), precision)
        return hull_vertices, [ (0, i+1, i+2)
                                for i in xrange(len(hull_vertices) - 2) ]
    elif len(hull_vertices) <= 2:
        # colinear or singular
        # no triangles for these cases
        return hull_vertices, []

    # construct list of triangles of this simplex
    hull_triangles = set([ operator.itemgetter(i,j,k)(hull_vertices)
                         for i, j, k in ((1,0,2), (0,1,3), (0,3,2), (3,1,2)) ])

    if verbose:
        lx.out("starting set", hull_vertices)

    # construct list of outer vertices for each triangle
    outer_vertices = {}
    for triangle in hull_triangles:
        outer = \
            [ (dist, vert)
              for dist, vert
              in izip( ( vecDistanceTriangle(triangle, vert)
                         for vert in vertices ),
                       vertices )
              if dist > precision ]
        if outer:
            outer_vertices[triangle] = outer

    # as long as there are triangles with outer vertices
    while outer_vertices:
        # grab a triangle and its outer vertices
        tmp_iter = outer_vertices.iteritems()
        triangle, outer = tmp_iter.next() # tmp_iter trick to make 2to3 work
        # calculate pivot point
        pivot = max(outer)[1]
        if verbose:
            lx.out("pivot", pivot)
        # add it to the list of extreme vertices
        hull_vertices.append(pivot)
        # and update the list of triangles:
        # 1. calculate visibility of triangles to pivot point
        visibility = [ vecDistanceTriangle(othertriangle, pivot) > precision
                       for othertriangle in outer_vertices.iterkeys() ]
        # 2. get list of visible triangles
        visible_triangles = [ othertriangle
                              for othertriangle, visible
                              in izip(outer_vertices.iterkeys(), visibility)
                              if visible ]
        # 3. find all edges of visible triangles
        visible_edges = []
        for visible_triangle in visible_triangles:
            visible_edges += [operator.itemgetter(i,j)(visible_triangle)
                              for i, j in ((0,1),(1,2),(2,0))]
        if verbose:
            lx.out("visible edges", visible_edges)
        # 4. construct horizon: edges that are not shared with another triangle
        horizon_edges = [ edge for edge in visible_edges
                          if not tuple(reversed(edge)) in visible_edges ]
        # 5. remove visible triangles from list
        # this puts a hole inside the triangle list
        visible_outer = set()
        for outer_verts in outer_vertices.itervalues():
            visible_outer |= set(map(operator.itemgetter(1), outer_verts))
        for triangle in visible_triangles:
            if verbose:
                lx.out("removing", triangle)
            hull_triangles.remove(triangle)
            del outer_vertices[triangle]
        # 6. close triangle list by adding cone from horizon to pivot
        # also update the outer triangle list as we go
        for edge in horizon_edges:
            newtriangle = edge + ( pivot, )
            newouter = \
                [ (dist, vert)
                  for dist, vert in izip( ( vecDistanceTriangle(newtriangle,
                                                                vert)
                                            for vert in visible_outer ),
                                          visible_outer )
                  if dist > precision ]
            hull_triangles.add(newtriangle)
            if newouter:
                outer_vertices[newtriangle] = newouter
            if verbose:
                lx.out("adding", newtriangle, newouter)

    # no triangle has outer vertices anymore
    # so the convex hull is complete!
    # remap the triangles to indices that point into hull_vertices
    return hull_vertices, [ tuple(hull_vertices.index(vert)
                                  for vert in triangle)
                            for triangle in hull_triangles ]

def linePlaneIntersection(ray_normal,ray_pos,plane_normal,plane_pos,backfaces=False,reverse=False):
    w0 = vecSub(ray_pos, plane_pos)
    a = -vecDotProduct(plane_normal,w0)
    b = vecDotProduct(plane_normal,ray_normal)
    if b > 0 and not backfaces:  #ignore backfaces
        return None
    if abs(b) < 0.0000001: #ignore faces parrellel to ray
        return None
    r = a / b;
    if r < 0 and not reverse:
        return None                 
    return vecAdd(ray_pos,vecScalarMul(ray_normal, r))
    
def rayTriIntersection (ray, pos, tris, tri_normals, backfaces = False):
    indicies = []
    intersections = []
    for i in range(len(tris)):
        u = vecSub(tris[i][1],tris[i][0])
        v = vecSub(tris[i][2],tris[i][0])
        w0 = vecSub(pos, tris[i][0])
        a = -vecDotProduct(tri_normals[i],w0)
        b = vecDotProduct(tri_normals[i],ray)
        if not backfaces:  #ignore backfaces
            if b > 0:
                continue
        if abs(b) < 0.0000001: #ignore faces parrellel to ray
            continue
        r = a / b;
        if (r < 0):
            continue                  
        intersection = vecAdd(pos,vecScalarMul(ray, r)) 
        uu = vecDotProduct(u,u)
        uv = vecDotProduct(u,v)
        vv = vecDotProduct(v,v)
        w = vecSub(intersection, tris[i][0])
        wu = vecDotProduct(w,u)
        wv = vecDotProduct(w,v)
        D = uv * uv - uu * vv
        s = (uv * wv - vv * wu) / D
        
        if (s < 0.0 or s > 1.0):       
            continue
        t = (uv * wu - uu * wv) / D
        if (t < 0.0 or (s + t) > 1.0):  
            continue
        indicies.append(i)
        intersections.append(intersection)

    return (indicies,   intersections)


def matrix3Rotate(matrix, vec):
    return  [ matrix[0][0]*vec[0] + matrix[0][1]*vec[1] + matrix[0][2]*vec[2], \
              matrix[1][0]*vec[0] + matrix[1][1]*vec[1] + matrix[1][2]*vec[2], \
              matrix[2][0]*vec[0] + matrix[2][1]*vec[1] + matrix[2][2]*vec[2] ]

def matrixMultiply(matrix1,matrix2):
    # Matrix multiplication
    if len(matrix1[0]) != len(matrix2):
        # Check matrix dimensions
        raise ValueError ("Matrix dimensions are not equal")
    else:
        # Multiply if correct dimensions
        new_matrix = zero(len(matrix1),len(matrix2[0]))
        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix2)):
                    new_matrix[i][j] += matrix1[i][k]*matrix2[k][j]
        return new_matrix

def matrixToEular (matrix, degrees=False):
    x = matrix[0]
    y = matrix[1]
    z = matrix[2]


    if y[0] > 0.998:
        heading = atan2(x[2],z[2])
        altitude = asin(y[0])
        bank = 0
    elif y[0] < -0.998:
        heading = atan2(x[2],z[2])
        altitude = asin(y[0])
        bank = 0
    else:                                               
        heading = atan2(-z[0],x[0])
        altitude = asin(y[0])
        bank = atan2(-y[2],y[1])			
    
    if degrees:
        return (math.degrees(heading),math.degrees(altitude),math.degrees(bank))
    return (heading,altitude,bank)

def area3D_Polygon( verts, normal ):
    # wrap around verts
    verts.append(verts[0])
    verts.append(verts[1])
    # get unit vector of normal
    normal = vecNormalized(normal)
    
    area = 0

    ax = abs(normal[0])     # abs x-coord
    ay = abs(normal[1])     # abs y-coord
    az = abs(normal[2])     # abs z-coord
    coord = 3                   
    if (ax > ay):
        if (ax > az):
            coord = 1   
    elif (ay > az):
        coord = 2 
    for i in range(len(verts) - 2):
        if coord ==  1:
            area = area + (verts[i+1][1] * (verts[i+2][2] - verts[i][2]))
            continue
        if coord ==  2:
            area = area + (verts[i+1][0] * (verts[i+2][2] - verts[i][2]))
            continue
        if coord == 3:
            area = area + (verts[i+1][0] * (verts[i+2][1] - verts[i][1]))
            continue
    
    # scale to get area before projection
    an = math.sqrt( ax*ax + ay*ay + az*az )# length of normal vector
    if coord ==  1:
        area = area * (an / (2*ax))
    if coord ==  2:
        area = area * (an / (2*ay))
    if coord ==  3:
        area = area * (an / (2*az))
    return abs(area)

def vectorMatrix(vec):
    imin = 0
    for i in range(len(vec)):
        if(abs(vec[i]) < abs(vec[imin])):
            imin = i

    vec2 = [0,0,0]
    dt = vec[imin]

    vec2[imin] = 1
    for i in range(len(vec)):
        vec2[i] -= dt*vec[i]
     
    vec3 = vecCrossProduct(vec,vec2)
    return (vec,tuple(vec2),vec3)

def orientMatrix(matrix,keep_X=False,keep_Y=False,keep_Z=False):
    new_matrix = list(matrix)
    sorted_x = sorted(matrix, key=lambda idx: abs(idx[0]))
    sorted_y = sorted(matrix, key=lambda idx: abs(idx[1]))
    sorted_z = sorted(matrix, key=lambda idx: abs(idx[2]))
    
    if keep_X == False:
        new_matrix[0] = sorted_x[2]
    if keep_Y == False:
        new_matrix[1] = sorted_y[2]
    if keep_Z == False:
        new_matrix[2] = sorted_z[2]
        
    a = b = c = 1
    while new_matrix[0] == new_matrix[1] or new_matrix[1] == new_matrix[2] or new_matrix[0] == new_matrix[2]:
        if a == 3:
            a = 0
        if b == 3:
            b = 0
        if c == 3:
            c = 0
        if abs(new_matrix[0][0]) >= abs(new_matrix[1][1]) and keep_Y == False:
            new_matrix[1] = sorted_y[b]
            b = b+1
        if abs(new_matrix[1][1]) >= abs(new_matrix[0][0]) and keep_X == False:
            new_matrix[0] = sorted_x[a]
            a = a+1
        if abs(new_matrix[1][1]) >= abs(new_matrix[2][2]) and keep_Z == False:
            new_matrix[2] = sorted_z[c]
            c = c+1
        if abs(new_matrix[2][2]) >= abs(new_matrix[1][1]) and keep_Y == False:
            new_matrix[1] = sorted_y[b]
            b = b+1
        if abs(new_matrix[2][2]) >= abs(new_matrix[0][0]) and keep_X == False:
            new_matrix[0] = sorted_x[a]
            a = a+1
        if abs(new_matrix[0][0]) >= abs(new_matrix[2][2]) and keep_Z == False:
            new_matrix[2] = sorted_z[c]
            c = c+1
            
    if new_matrix[0][0] < 0:
        new_matrix[0] =(-new_matrix[0][0],-new_matrix[0][1],-new_matrix[0][2])
    if new_matrix[1][1] < 0:
        new_matrix[1] =(-new_matrix[1][0],-new_matrix[1][1],-new_matrix[1][2])
    if new_matrix[2][2] < 0:
        new_matrix[2] =(-new_matrix[2][0],-new_matrix[2][1],-new_matrix[2][2])
    return tuple(new_matrix)

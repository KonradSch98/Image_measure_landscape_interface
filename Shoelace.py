
def shoelace(polygonBoundary):
    """
    implementation of shoelace algorithm for space calculation of arbitrary polygon

    Args:
        polygonBoundary (list): double list [[x],[y]] of x and y coord. of the polygon vertices 

    Returns:
        pix_space (float): the total pixel number of the polygon's space
    """
    
    
    
    np1_vertex = len(polygonBoundary[0])
    n_vertex = np1_vertex - 1        
    dobl_space = [(polygonBoundary[0][i] - polygonBoundary[0][i+1]) * (polygonBoundary[1][i+1] + polygonBoundary[1][i]) for i in range(n_vertex)]
    return abs(sum(dobl_space) / 2)

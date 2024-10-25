def max_sum_of_submatrices(matrix):
    m = len(matrix)
    n = len(matrix[0]) if m > 0 else 0

    # Step 1: Create and fill the prefix sum matrix
    prefix_sum = [[0] * n for _ in range(m)]
    
    # Calculate prefix sums
    for i in range(m):
        for j in range(n):
            prefix_sum[i][j] = matrix[i][j]
            if i > 0:
                prefix_sum[i][j] += prefix_sum[i - 1][j]
            if j > 0:
                prefix_sum[i][j] += prefix_sum[i][j - 1]
            if i > 0 and j > 0:
                prefix_sum[i][j] -= prefix_sum[i - 1][j - 1]

    # Helper function to get sum of submatrix (x1, y1) to (x2, y2)
    def get_submatrix_sum(x1, y1, x2, y2):
        result = prefix_sum[x2][y2]
        if x1 > 0:
            result -= prefix_sum[x1 - 1][y2]
        if y1 > 0:
            result -= prefix_sum[x2][y1 - 1]
        if x1 > 0 and y1 > 0:
            result += prefix_sum[x1 - 1][y1 - 1]
        return result

    # Step 2: Iterate over all possible ways to split the matrix
    max_result = float('-inf')
    best_r, best_c = 0, 0  # To store the best r and c that give the max result
    for r in range(m - 1):
        for c in range(n - 1):
            # Calculate sums for each of the four submatrices
            top_left = get_submatrix_sum(0, 0, r, c)
            top_right = get_submatrix_sum(0, c + 1, r, n - 1)
            bottom_left = get_submatrix_sum(r + 1, 0, m - 1, c)
            bottom_right = get_submatrix_sum(r + 1, c + 1, m - 1, n - 1)

            # Calculate the result as the sum of the absolute values
            result = abs(top_left) + abs(top_right) + abs(bottom_left) + abs(bottom_right)

            # Track the maximum result and the position of (r, c)
            if result > max_result:
                max_result = result
                best_r, best_c = r, c

    return max_result, best_r, best_c

print(max_sum_of_submatrices([[3, 0, 2, -8, -8],
                             [5, 3, 2, 2, 3],
                             [2, 5, 2, 1, 4],
                             [3, 4, -1, 4, 2],
                             [-3, 6, 2, 4, 3]]))

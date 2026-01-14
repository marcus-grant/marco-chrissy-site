# Pagination Performance Comparison

Benchmark results comparing different `photos_per_page` values for the wedding gallery (645 photos).

## Test Configuration

- **Photo count**: 645
- **Thumbnail size**: 400px
- **Quality**: 85
- **Theme**: minimal

## Results Summary

| photos_per_page | Build (s) | Pages | HTML Total | First Page | Perf | FCP (ms) | LCP (ms) | CLS |
|-----------------|-----------|-------|------------|------------|------|----------|----------|-------|
| 20 | 359.96 | 34 | 217,492 | 6,642 | 72 | 902 | 3,230 | 0.512 |
| 50 | 363.57 | 14 | 199,692 | 15,372 | 77 | 1,052 | 1,277 | 0.667 |
| 100 | 364.29 | 8 | 194,354 | 29,929 | 77 | 1,052 | 1,052 | 0.667 |
| 200 | 350.66 | 5 | 191,699 | 59,037 | 76 | 1,202 | 2,027 | 0.667 |
| 300 | 349.23 | 4 | 190,814 | 88,137 | 76 | 1,352 | 2,177 | 0.667 |
| 500 | 361.44 | 3 | 189,929 | 146,337 | 73 | 1,653 | 2,553 | 0.667 |

## Observations

### Build Time

Build times are consistent (~350-365s) regardless of pagination. Thumbnail generation dominates build time, not HTML generation.

### Performance Score

- **20 photos/page**: 72 (lowest) - more HTTP requests for navigation
- **50-100 photos/page**: 77 (highest) - sweet spot
- **200-300 photos/page**: 76 - slight decrease

### Largest Contentful Paint (LCP)

- **20 photos/page**: 3,230ms (worst) - many small pages, but slower LCP
- **50-100 photos/page**: 1,052-1,277ms (best)
- **200-300 photos/page**: 2,027-2,177ms - larger pages hurt LCP

### Cumulative Layout Shift (CLS)

CLS is consistently 0.667 for all except 20 (0.512). This is a separate issue - images need explicit dimensions.

### HTML Size Trade-offs

- More pages = more total HTML (navigation overhead per page)
- Fewer pages = larger individual pages but less total HTML

## Initial Recommendations

**Optimal range: 50-100 photos per page**

- Best Lighthouse performance scores (77)
- Best LCP times (~1,052ms)
- Reasonable page sizes
- Good balance of navigation vs load time

**Avoid extremes:**
- <50: Too many pages, slower LCP due to navigation overhead
- >200: Individual pages too large, LCP suffers

## Future Work

- Add lazy loading (native `loading="lazy"` or JS-based)
- Compare infinite scroll vs pagination
- Fix CLS with explicit image dimensions

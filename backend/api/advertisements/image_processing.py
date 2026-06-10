from imagekit.processors import ResizeToFill, ResizeToFit
from imagekit import ImageSpec
from imagekit.cachefiles import ImageCacheFile

class ProductImageProcessor:
    """
    Image processing utilities for product images.
    """
    
    @staticmethod
    def get_image_sizes(image_field):
        """
        Generate different sizes of images on-the-fly with caching.
        """
        # Define image specifications
        specs = {
            'thumbnail': ImageSpec(
                processors=[ResizeToFill(150, 150)],
                format='JPEG',
                options={'quality': 60}
            ),
            'card': ImageSpec(
                processors=[ResizeToFill(300, 200)],
                format='JPEG',
                options={'quality': 75}
            ),
            'modal': ImageSpec(
                processors=[ResizeToFit(600, 400)],
                format='JPEG',
                options={'quality': 80}
            ),
            'large': ImageSpec(
                processors=[ResizeToFit(1200, 800)],
                format='JPEG',
                options={'quality': 90}
            )
        }
        
        sizes = {}
        for size_name, spec in specs.items():
            # Create cached image file
            cache_file = ImageCacheFile(spec, name=f"{image_field.name}_{size_name}")
            cache_file.generate()
            sizes[size_name] = cache_file.url
        
        # Original image
        sizes['original'] = image_field.url
        
        return sizes
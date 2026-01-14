from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
from django.conf import settings
from django.utils.safestring import mark_safe

@dataclass
class SeoData:
    title: str
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    canonical_url: Optional[str] = None
    og_type: str = "website"
    twitter_card: str = "summary_large_image"
    twitter_creator: Optional[str] = None
    json_ld: Optional[Dict[str, Any]] = None
    
    # Extra fields for flexibility
    extra_meta: Dict[str, str] = field(default_factory=dict)

    def get_json_ld_script(self):
        if not self.json_ld:
            return ""
        return mark_safe(f'<script type="application/ld+json">{json.dumps(self.json_ld)}</script>')

class SeoViewMixin:
    """
    Mixin to handle SEO data generation for views.
    """
    seo_title = None
    seo_description = None
    
    def get_seo_object(self):
        """
        Return the object to extract SEO data from.
        Defaults to self.object if available (DetailView).
        """
        if hasattr(self, 'object') and self.object:
            return self.object
        return None

    def get_seo_data(self, context) -> SeoData:
        obj = self.get_seo_object()
        
        # Default values from View attributes or global defaults
        title = f"{self.seo_title} - GourmetWiki - Deine #1 Wissensküche" or "GourmetWiki"
        description = self.seo_description or ""
        keywords = []
        image_url = None
        canonical_url = self.request.build_absolute_uri()
        json_ld = None
        twitter_creator = "@GourmetWiki"
        
        # If object has get_seo_data method, use it
        if obj and hasattr(obj, 'get_seo_data'):
            obj_seo = obj.get_seo_data(self.request)
            return obj_seo
            
        # Fallback logic if object exists but no explicit SEO method
        if obj:
            if hasattr(obj, 'name'):
                title = obj.name
            elif hasattr(obj, 'title'):
                title = obj.title
                
            if hasattr(obj, 'description') and obj.description:
                description = obj.description
                
            if hasattr(obj, 'get_absolute_url'):
                canonical_url = self.request.build_absolute_uri(obj.get_absolute_url())

        return SeoData(
            title=title,
            description=description,
            keywords=keywords,
            image_url=image_url,
            canonical_url=canonical_url,
            twitter_creator=twitter_creator
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seo_data = self.get_seo_data(context)
        
        # Inject into context
        context['seo'] = seo_data
        
        # Backwards compatibility / Direct access in templates
        context['page_title'] = seo_data.title
        context['page_description'] = seo_data.description
        context['page_keywords'] = ", ".join(seo_data.keywords)
        context['og_title'] = seo_data.title
        context['og_description'] = seo_data.description
        context['og_image'] = seo_data.image_url
        context['og_type'] = seo_data.og_type
        context['twitter_title'] = seo_data.title
        context['twitter_description'] = seo_data.description
        context['twitter_image'] = seo_data.image_url
        context['twitter_creator'] = seo_data.twitter_creator
        context['canonical_url'] = seo_data.canonical_url
        
        if seo_data.json_ld:
             context['json_ld_data'] = seo_data.json_ld
             
        return context

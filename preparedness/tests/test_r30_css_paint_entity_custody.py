"""R30 synthetic-only source visibility regression cases. No release or safety PASS."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import citation_token_visibility_gate as gate

BAD_STYLES = [('clip_path_inset', 'clip-path:inset(50%)'), ('clip_path_polygon', 'clip-path:polygon(0 0,0 0,0 0)'), ('clip_path_circle', 'clip-path:circle(0)'), ('clip_rectangle', 'clip:rect(0,0,0,0)'), ('mask_image_linear', 'mask-image:linear-gradient(transparent,transparent)'), ('mask_image_none_alternate', 'mask-image:url(#hide)'), ('mask_shorthand', 'mask:linear-gradient(transparent,transparent)'), ('webkit_mask', '-webkit-mask:linear-gradient(transparent,transparent)'), ('webkit_mask_image', '-webkit-mask-image:url(#transparent)'), ('filter_opacity', 'filter:opacity(0)'), ('filter_blur', 'filter:blur(999px)'), ('filter_brightness', 'filter:brightness(0)'), ('webkit_filter_opacity', '-webkit-filter:opacity(0%)'), ('transform_scale', 'transform:scale(0)'), ('transform_scale_decimal', 'transform:scale(0.00)'), ('transform_scalex', 'transform:scaleX(0)'), ('transform_scaley', 'transform:scaleY(0)'), ('scale_property', 'scale:0'), ('width_zero_px', 'width:0px'), ('height_zero', 'height:0'), ('min_width_zero', 'min-width:0'), ('min_height_zero', 'min-height:0px'), ('max_width_zero', 'max-width:0px'), ('max_height_zero', 'max-height:0px'), ('block_size_zero', 'block-size:0'), ('inline_size_zero', 'inline-size:0px'), ('max_block_size_zero', 'max-block-size:0px'), ('max_inline_size_zero', 'max-inline-size:0px'), ('overflow_hidden', 'overflow:hidden'), ('overflow_clip', 'overflow:clip'), ('overflow_x_hidden', 'overflow-x:hidden'), ('overflow_y_clip', 'overflow-y:clip'), ('text_indent_negative', 'text-indent:-9999px'), ('left_negative', 'left:-9999px'), ('right_negative', 'right:-2px'), ('top_negative', 'top:-2em'), ('bottom_negative', 'bottom:-50%'), ('color_rgba_zero', 'color:rgba(0,0,0,0)'), ('color_rgba_decimal_zero', 'color:rgba(255,0,0,0.00)'), ('color_rgb_slash_zero', 'color:rgb(255 255 255 / 0)'), ('color_hsla_zero', 'color:hsla(0,100%,50%,0)'), ('color_hsl_slash_zero', 'color:hsl(0 100% 50% / 0)'), ('color_oklch_slash_zero', 'color:oklch(50% .1 20 / 0)'), ('color_hex_four_zero', 'color:#fff0'), ('color_hex_eight_zero', 'color:#abcdef00'), ('webkit_text_fill', '-webkit-text-fill-color:transparent'), ('webkit_fill_rgba', '-webkit-text-fill-color:rgba(255,0,0,0)'), ('line_height_zero', 'line-height:0'), ('line_height_zero_em', 'line-height:0em'), ('zoom_zero', 'zoom:0'), ('zoom_zero_percent', 'zoom:0%'), ('opacity_var', 'opacity:var(--hidden)'), ('opacity_calc', 'opacity:calc(0)'), ('width_var', 'width:var(--size)'), ('max_height_calc', 'max-height:calc(1px - 1px)'), ('color_var', 'color:var(--ink)'), ('display_var', 'display:var(--mode)'), ('visibility_env', 'visibility:env(hidden, visible)'), ('opacity_clamp', 'opacity:clamp(0,0,0)'), ('opacity_min', 'opacity:min(0, 1)'), ('opacity_max', 'opacity:max(0, 0)'), ('css_escaped_clip', 'cl\\69 p-path:inset(50%)'), ('css_escaped_mask', 'ma\\73 k-image:url(#hidden)'), ('css_escaped_filter', 'fi\\6c ter:opacity(0)'), ('css_escaped_color', 'color:r\\67 ba(0,0,0,0)'), ('css_comment_mask', 'mask:/* hidden */url(#hidden)'), ('css_comment_opacity', 'opacity:/**/calc(0)')]

BAD_ENTITIES = [('numeric_decimal', '&#123;&#123;cite:source&#125;&#125;'), ('numeric_hex', '&#x7b;&#x7b;cite:source&#x7d;&#x7d;'), ('named_lbrace', '&lbrace;&lbrace;cite:source&rbrace;&rbrace;'), ('named_lcub', '&lcub;&lcub;cite:source&rcub;&rcub;'), ('left_only', '&#123;&#123;cite:source}}'), ('right_only', '{{cite:source&#125;&#125;'), ('mixed_left', '&#x7b;&lbrace;cite:source}}'), ('mixed_right', '{{cite:source&rbrace;&#125;'), ('partial_cite_entity', '{{c&#105;te:source}}'), ('partial_cite_entity_hex', '{{cit&#x65;:source}}'), ('partial_id_entity', '{{cite:s&#111;urce}}'), ('partial_brace_in_text', 'Claim &#123;&#123;cite:source}}'), ('casefold_decode', '&#123;&#123;Cite:source&#125;&#125;'), ('decoded_malformed', '&#123;&#123;cite: source&#125;&#125;'), ('encoded_comment', '<!-- &#123;&#123;cite:source&#125;&#125; -->'), ('encoded_attribute', '<span title="&#123;&#123;cite:source&#125;&#125;">Hi</span>'), ('encoded_script', '<script>let a="&#123;&#123;cite:source&#125;&#125;"</script>'), ('encoded_plus_literal', '{{cite:a}} &#123;&#123;cite:b&#125;&#125;'), ('encoded_plus_literal_same', '{{cite:a}} &#123;&#123;cite:a&#125;&#125;'), ('extra_decoded_prefix', '{{cite:a}} &lcub;&lcub;cite')]

ACCEPT_STYLES = [('plain', 'color:black'), ('opaque_rgba', 'color:rgba(0,0,0,1)'), ('opaque_hsla', 'color:hsla(200,100%,50%,1)'), ('hex_opaque', 'color:#000f'), ('rgb_slash_opaque', 'color:rgb(0 0 0 / 1)'), ('font_14', 'font-size:14px'), ('line_height_20', 'line-height:20px'), ('zoom_1', 'zoom:1'), ('opacity_one', 'opacity:1'), ('opacity_half', 'opacity:0.5'), ('width_100', 'width:100%'), ('height_100', 'height:100px'), ('min_width_2', 'min-width:2rem'), ('max_width_80', 'max-width:80vw'), ('overflow_visible', 'overflow:visible'), ('overflow_auto', 'overflow:auto'), ('filter_none', 'filter:none'), ('webkit_filter_none', '-webkit-filter:none'), ('clip_path_none', 'clip-path:none'), ('clip_auto', 'clip:auto'), ('mask_none', 'mask:none'), ('mask_image_none', 'mask-image:none'), ('transform_rotate', 'transform:rotate(2deg)'), ('transform_scale_one', 'transform:scale(1)'), ('left_positive', 'left:2px'), ('text_indent_positive', 'text-indent:2px'), ('position_relative', 'position:relative'), ('content_visibility_visible', 'content-visibility:visible')]


class RejectStyles(unittest.TestCase): pass
for label,style in BAD_STYLES:
    def check(self,style=style):
        html='<section style="'+style+'"><p>Evidence {{cite:source}}</p></section>'
        with self.assertRaises(gate.CitationPlacementHold): gate.verified_citations(html)
    setattr(RejectStyles,'test_'+label,check)

class RejectEntities(unittest.TestCase): pass
for label,raw in BAD_ENTITIES:
    def check(self,raw=raw):
        with self.assertRaises(gate.CitationPlacementHold): gate.verified_citations('<p>'+raw+'</p>')
    setattr(RejectEntities,'test_'+label,check)

class AcceptStyles(unittest.TestCase): pass
for label,style in ACCEPT_STYLES:
    def check(self,style=style):
        body='<p style="'+style+'">Proof {{cite:source}}</p>'
        hits=gate.verified_citations(body)
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0].start(),body.index('{{cite:source}}'))
    setattr(AcceptStyles,'test_'+label,check)

class StructuralAndEthicalBounds(unittest.TestCase):
    def test_repeated_source_ids_remain_individual_occurrences(self):
        self.assertEqual([m.group(1) for m in gate.verified_citations('<p>{{cite:x}}/{{cite:x}}/{{cite:y}}</p>')],['x','x','y'])
    def test_unicode_offset_not_rebased_after_entity(self):
        s='⚓ &copy; 🔎 <p>{{cite:x}}</p>'
        self.assertEqual(gate.verified_citations(s)[0].start(),s.index('{{cite:x}}'))
    def test_visible_token_with_hidden_sibling_rejected(self):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations('<p>{{cite:ok}}</p><p style="mask-image:url(#x)">{{cite:hidden}}</p>')
    def test_visible_token_with_decoded_fake_rejected(self):
        with self.assertRaises(gate.CitationPlacementHold):
            gate.verified_citations('<p>{{cite:ok}} &#123;&#123;cite:fake&#125;&#125;</p>')
    def test_browser_verification_remains_release_hold(self):
        self.assertIn('release HOLD',gate.__doc__)
    def test_true_type_guard(self):
        with self.assertRaises(gate.CitationPlacementHold): gate.verified_citations(b'{{cite:x}}')

# Stash Plugin: Performer Body Calculator 

This plugin will tag performers based on existing metadata within Stash.

If the `Measurements` attribute is present, it will be used to calculate the performer's body part sizes and body shape. The following formats are supported:
- `32D-28-34` (Bra Size, Waist, Hips)
- `36-28-34` (Bust, Waist, Hips)
- `32D` (Bra Size)
- `32D (70D)` (Bra Size with Alternate Units)

If the `Height` and `Weight` attributes are both present, they will be used to calculate the performer's body type.

### Tags
The tags will be generated or will use existing tags if there exists a tag with a matching name. The tag names can be customized by changing the first parameter of the `StashTagDC` input in `body_tags.py`
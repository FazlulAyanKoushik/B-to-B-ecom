def get_tag_slug(instance):
    return "%s-%s" % (instance.category, instance.name)

def get_address_slug(instance):
    return "%s %s %s" % (
        instance.post_office,
        instance.police_station,
        instance.district.name,
    )

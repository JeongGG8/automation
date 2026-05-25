from .models import Menu, RoleMenu


def sidebar_menus(request):
    if not request.user.is_authenticated:
        return {'sidebar_menus': []}

    parents = Menu.objects.filter(parent=None).prefetch_related('children').order_by('id')

    if request.user.is_staff:
        result = [
            {'menu': parent, 'children': list(parent.children.order_by('id'))}
            for parent in parents
        ]
        return {'sidebar_menus': result}

    if not request.user.role:
        return {'sidebar_menus': []}

    allowed_ids = set(
        RoleMenu.objects.filter(role=request.user.role).values_list('menu_id', flat=True)
    )

    result = []
    for parent in parents:
        children = [c for c in parent.children.order_by('id') if c.id in allowed_ids]
        if children or parent.id in allowed_ids:
            result.append({'menu': parent, 'children': children})

    return {'sidebar_menus': result}

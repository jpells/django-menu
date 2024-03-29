from menu.models import Menu, MenuItem  
from django import template  

register = template.Library()  
   
def build_menu(parser, token):  
    """ 
    {% menu menu_name %} 
    """  
    try:  
        tag_name, menu_name = token.split_contents()  
    except:  
        raise template.TemplateSyntaxError, "%r tag requires exactly one argument" % token.contents.split()[0]  
    return MenuObject(menu_name)  
   
class MenuObject(template.Node):  
    def __init__(self, menu_name):  
        self.menu_name = menu_name  
   
    def render(self, context):  
        current_path = template.resolve_variable('request.path', context)  
        user = template.resolve_variable('user', context)  
        context['menuitems'] = get_items(self.menu_name, current_path, user)  
        return ''  
     
def build_sub_menu(parser, token):  
    """ 
    {% submenu %} 
    """  
    return SubMenuObject()  
   
class SubMenuObject(template.Node):  
    def __init__(self):  
        pass  
   
    def render(self, context):  
        current_path = template.resolve_variable('request.path', context)  
        user = template.resolve_variable('user', context)  
        menu = False  
        for m in Menu.objects.filter(base_url__isnull=False):  
            if m.base_url and current_path.startswith(m.base_url):  
                menu = m  
   
        if menu:  
            context['submenu_items'] = get_items(menu.slug, current_path, user)  
            context['submenu'] = menu  
        else:  
            context['submenu_items'] = context['submenu'] = None  
        return ''  
   
def get_items(menu, current_path, user):  
    menuitems = []  
    for i in MenuItem.objects.filter(menu__slug=menu).order_by('order'):  
        i.current = ( i.link_url != '/' and current_path.startswith(i.link_url)) or ( i.link_url == '/' and current_path == '/' )  
        if (not i.staff_required or (i.staff_required and user.is_staff)) and (not i.login_required or (i.login_required and user.is_authenticated)):
            menuitems.append(i)
    return menuitems  
   
register.tag('menu', build_menu)  
register.tag('submenu', build_sub_menu)  

from  browser import html





def create_pacman():
    
    body = html.DIV(Class='pacman')
    body <= html.DIV(Class='pacman__eye')
    body <= html.DIV(Class='pacman__mouth')
    body <= html.DIV(Class='food pacman__food')
    body <= html.DIV(Class='pacman__tail')
    
    return body
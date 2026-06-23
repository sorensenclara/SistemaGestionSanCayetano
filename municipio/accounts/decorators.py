from django.contrib.auth.decorators import user_passes_test


def es_ciudadano(user):
    return user.is_authenticated and user.is_ciudadano()


def es_operador(user):
    return user.is_authenticated and user.is_operador()


def es_funcionario(user):
    return user.is_authenticated and user.is_funcionario()


def es_admin(user):
    return user.is_authenticated and user.is_administrador()


def es_usuario_interno(user):
    return (
        user.is_authenticated
        and not user.is_ciudadano()
    )


ciudadano_required = user_passes_test(
    es_ciudadano,
    login_url="/ciudadano/login/"
)

interno_required = user_passes_test(
    es_usuario_interno,
    login_url="/login/"
)
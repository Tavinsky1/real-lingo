# translations.py
# Translation dictionary for LingoWorld

TRANSLATIONS = {
    'en': {
        # Navigation
        'explore': 'Explore',
        'random': 'Random',
        'change_country': 'Change Country',
        'change_language': 'Change Language',
        'choose_country': 'Choose Country',
        'all_terms': 'All Terms',
        'admin': 'Admin',
        'admin_panel': 'Admin Panel',
        'home': 'Home',
        
        # Country Selection
        'countries': 'Countries',
        'terms': 'Terms',
        'multi_lingual': 'Multi-lingual',
        'more_countries_coming': 'More Countries Coming Soon',
        
        # Entry Details
        'definition': 'Definition',
        'translations': 'Translations',
        'categories': 'Categories',
        'usage_examples': 'Usage Examples',
        'how_to_use': 'How to use "{term}"?',
        'in_conversation': 'In conversation',
        'in_context': 'In context',
        'related_terms': 'Related terms',
        'quick_actions': 'Quick actions',
        'add_to_favorites': 'Add to favorites',
        'remove_from_favorites': 'Remove from favorites', 
        'copy_term': 'Copy term',
        'share_term': 'Share term',
        'favorite': 'Favorite',
        'add': 'Add',
        'share': 'Share',
        'share_term': 'Share term',
        'copy_translation': 'Copy translation',
        'copy_translation_aria': 'Copy translation to clipboard',
        'pronounce': 'Pronounce',
        'random_term': 'Random term',
        'search_more_info': 'Search more info',
        'mark_as_learned': 'Mark as learned',
        'statistics': 'Statistics',
        'views': 'Views',
        'favorites': 'Favorites',
        'navigation': 'Navigation',
        'explore_more_terms': 'Explore more terms',
        'load_more': 'Load more',
        'search_placeholder': 'Search terms, definitions...',
        'search_button': 'Search',
        'search_aria': 'Search for terms or definitions',
        'language_select': 'Select Language:',
        'language_select_aria': 'Select Language',
        'exploring': 'Exploring:',
        'quick_quiz': 'Quick Quiz',
        'show_more_refresh': 'Show More / Refresh',
        'welcome_to_realling': 'Welcome to REAL LINGO',
        'discover_slang_world': 'Discover the fascinating world of slang from different countries. Choose your destination and dive into authentic local expressions!',
        'terms_count': '3,811+ Terms',
        'countries_count': '5 Countries',
        'free_forever': 'Free Forever',
        'choose_your_country': 'Choose Your Country',
        'explore_lingo_in': 'Explore Lingo in',
        'select_category': 'Select a category to discover slang, idioms, and more!',
        'link_copied': 'Link copied to clipboard',
        'copied_to_clipboard': 'Copied to clipboard',
        'browser_no_speech': 'Your browser does not support speech synthesis',
        'term_marked_learned': 'Term marked as learned!',
        'error_marking_learned': 'Error marking as learned',
        'login_required_progress': 'You need to log in to save your progress',
        'entry_header_term': 'Term: {term}',
        'search_country_slang': 'Search {country} Slang',
        'search_placeholder_argentina': 'Enter a lunfardo term...',
        'search_placeholder_australia': 'Enter an Aussie term...',
        'search_placeholder_germany': 'Enter a German slang term...',
        'search_placeholder_colombia': 'Enter a Colombian term...',
        'search_placeholder_belgium': 'Enter a Belgian term...',
        'search_terms_title': 'Search terms',
        'search_terms_aria': 'Search for terms',
        'random_terms': 'Random Terms',
        'browse_all': 'Browse All',
        'popular_categories': 'Popular Categories',
        'terms_available': 'terms available',
        'close': 'Close',
        
        # Authentication
        'login': 'Login',
        'logout': 'Logout',
        'signup': 'Sign Up',
        'sign_up': 'Sign Up',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'email': 'Email',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'welcome_back': 'Welcome back!',
        'login_to_continue': 'Log in to continue your learning journey',
        'create_account': 'Create Account',
        'join_lingoworld': 'Join LingoWorld and start contributing!',
        'already_have_account': 'Already have an account?',
        'dont_have_account': 'Don\'t have an account?',
        'login_here': 'Log in here',
        'signup_here': 'Sign up here',
        'login_success': 'Welcome back! You have successfully logged in.',
        'logout_success': 'You have been logged out successfully.',
        'signup_success': 'Account created successfully! Welcome to LingoWorld.',
        'login_required': 'Please log in to access this feature.',
        'invalid_credentials': 'Invalid username or password.',
        'account_created': 'Your account has been created successfully!',
        'password_mismatch': 'Passwords do not match.',
        'username_taken': 'This username is already taken.',
        'email_taken': 'This email is already registered.',
        'profile': 'Profile',
        'my_contributions': 'My Contributions',
        'my_favorites': 'My Favorites',
        'account_settings': 'Account Settings',
        'contributed_by': 'Contributed by',
        'added_by': 'Added by',
        'contributor': 'Contributor',
        'add_entry': 'Add Entry',
        'contribute': 'Contribute',
        'edit_entry': 'Edit Entry',
        'my_entries': 'My Entries',
        'my_profile': 'My Profile',
        'entries_contributed': 'Entries Contributed',
        'join_community': 'Join our community of language enthusiasts!',
        'added': 'Added',
        'updated': 'Updated',
        'browse_all': 'Browse All',
        'close': 'Close',
        
        # Email Verification
        'email_verification_subject': 'Verify your LingoWorld account',
        'verify_email_message': 'Please click the button below to verify your email address and activate your LingoWorld account.',
        'verify_email_button': 'Verify Email Address',
        'email_verification_pending': 'Check Your Email',
        'signup_success_verify_email': 'Account created successfully! Please check your email ({email}) for verification instructions.',
        'email_sending_failed': 'Failed to send verification email. Please try again.',
        'invalid_form_data': 'Please correct the errors below.',
        'invalid_verification_token': 'Invalid verification link. Please try again or request a new verification email.',
        'verification_token_expired': 'Verification link has expired. Please request a new verification email.',
        'email_already_verified': 'Your email is already verified. You can now log in.',
        'email_verification_success': 'Email verified successfully! Welcome to LingoWorld!',
        'verification_email_resent': 'Verification email sent successfully. Please check your inbox.',
        'user_not_found': 'No pending account found with that email address.',
        'resend_verification': 'Resend Verification Email',
        'resend_verification_instructions': 'Enter your email address to receive a new verification link.',
        'verification_pending_message': 'We\'ve sent a verification email to your address. Please check your inbox and click the verification link to activate your account.',
        'didnt_receive_email': 'Didn\'t receive the email?',
        'resend_email': 'Resend Email',
        
        # Country Descriptions
        'country_descriptions': {
            'argentina': 'Explore the passionate world of Lunfardo - the unique slang of Argentina',
            'australia': "G'day mate! Discover authentic Aussie slang from the Outback to the coast",
            'germany': 'Discover German slang from Berlin to Bavaria',
            'colombia': '¡Qué chimba! Experience the vibrant Colombian slang from Bogotá to the Caribbean coast',
            'belgium': 'Dag hé! Explore the linguistic richness of Belgium - from Flemish wit to Walloon warmth'
        },
        
        # Example Templates by Country
        'example_templates': {
            'argentina': {
                'conversation': "I heard a porteño say '{}' at the café yesterday...",
                'context': "The term '{}' is widely used throughout Buenos Aires and the Río de la Plata region."
            },
            'australia': {
                'conversation': "My Aussie mate said '{}' when we were at the beach...",
                'context': "You'll often hear '{}' used in pubs and barbecues across Australia."
            },
            'germany': {
                'conversation': "In Berlin, someone told me '{}' means...",
                'context': "The expression '{}' is particularly common in German youth culture."
            },
            'colombia': {
                'conversation': "A friend from Medellín taught me that '{}' is used when...",
                'context': "In Colombian Spanish, '{}' reflects the vibrant culture of the Caribbean coast."
            },
            'belgium': {
                'conversation': "While in Brussels, I learned that '{}' is a typical expression...",
                'context': "The word '{}' showcases Belgium's unique multilingual heritage."
            }
        },
        'welcome': 'WELCOME',
        'choose_language': 'Choose Your Language',
        'select_language_to_continue': 'Select your preferred language to continue',
        'english': 'English',
        'spanish': 'Spanish',
        'explore_global_slang_english': 'Explore global slang and expressions in English',
        'explore_global_slang_spanish': 'Explora jerga y expresiones globales en español',
        'argentina': 'Argentina',
        'australia': 'Australia',
        'germany': 'Germany',
        'colombia': 'Colombia',
        'belgium': 'Belgium',
        'talk_like_local': 'Talk like a local. Not like a textbook.',
        'explore_argentina': 'Explorar Argentina',
        'explore_australia': 'Explorar Australia', 
        'explore_germany': 'Explorar Alemania',
        'explore_colombia': 'Explorar Colombia',
        'explore_belgium': 'Explorar Bélgica',
        'popular_argentina': 'Popular: Lunfardo, Che, Boludo',
        'popular_australia': 'Popular: G\'day, Mate, Arvo',
        'popular_germany': 'Popular: Geil, Krass, Alter',
        'popular_colombia': 'Popular: Chimba, Parce, Bacano',
        'popular_belgium': 'Popular: Amai, Zot, Schoon',
    },
    'es': {
        # Navigation
        'explore': 'Explorar',
        'random': 'Aleatorio',
        'change_country': 'Cambiar País',
        'change_language': 'Cambiar Idioma',
        'choose_country': 'Elegir País',
        'all_terms': 'Todos los Términos',
        'admin': 'Admin',
        'admin_panel': 'Panel de Admin',
        'home': 'Inicio',
        
        # Country Selection
        'countries': 'Países',
        'terms': 'Términos',
        'multi_lingual': 'Multilingüe',
        'more_countries_coming': 'Más Países Próximamente',
        'choose_your_country': 'Elige Tu País',
        
        # Entry Details
        'definition': 'Definición',
        'translations': 'Traducciones',
        'categories': 'Categorías',
        'usage_examples': 'Ejemplos de uso',
        'how_to_use': '¿Cómo usar "{term}"?',
        'in_conversation': 'En conversación',
        'in_context': 'En contexto',
        'related_terms': 'Términos relacionados',
        'quick_actions': 'Acciones rápidas',
        'add_to_favorites': 'Agregar a favoritos',
        'remove_from_favorites': 'Quitar de favoritos',
        'copy_term': 'Copiar término',
        'share_term': 'Compartir término',
        'favorite': 'Favorito',
        'add': 'Agregar',
        'share': 'Compartir',
        'share_term': 'Compartir término',
        'copy_translation': 'Copiar traducción',
        'copy_translation_aria': 'Copiar traducción al portapapeles',
        'pronounce': 'Pronunciar',
        'random_term': 'Término aleatorio',
        'search_more_info': 'Buscar más info',
        'mark_as_learned': 'Marcar como aprendido',
        'statistics': 'Estadísticas',
        'views': 'Vistas',
        'favorites': 'Favoritos',
        'navigation': 'Navegación',
        'explore_more_terms': 'Explorá más términos',
        'load_more': 'Cargar más',
        'search_placeholder': 'Buscar términos, definiciones...',
        'search_button': 'Buscar',
        'search_aria': 'Buscar términos o definiciones',
        'language_select': 'Seleccionar idioma:',
        'language_select_aria': 'Seleccionar idioma',
        'exploring': 'Explorando:',
        'quick_quiz': 'Quiz rápido',
        'show_more_refresh': 'Mostrar más / Actualizar',
        'welcome_to_realling': 'Bienvenido a REAL LINGO',
        'discover_slang_world': 'Descubre el fascinante mundo de la jerga de diferentes países. ¡Elige tu destino y sumérgete en expresiones locales auténticas!',
        'terms_count': '3,811+ Términos',
        'countries_count': '5 Países',
        'free_forever': 'Gratis para siempre',
        'choose_your_country': 'Elegí tu país',
        'explore_lingo_in': 'Explorar jerga en',
        'select_category': '¡Selecciona una categoría para descubrir jerga, modismos y más!',
        'link_copied': 'Enlace copiado al portapapeles',
        'copied_to_clipboard': 'Copiado al portapapeles',
        'browser_no_speech': 'Tu navegador no soporta síntesis de voz',
        'term_marked_learned': '¡Término marcado como aprendido!',
        'error_marking_learned': 'Error al marcar como aprendido',
        'login_required_progress': 'Necesitás iniciar sesión para guardar tu progreso',
        'entry_header_term': 'Término: {term}',
        'search_country_slang': 'Buscar jerga de {country}',
        'search_placeholder_argentina': 'Ingresa un término lunfardo...',
        'search_placeholder_australia': 'Ingresa un término australiano...',
        'search_placeholder_germany': 'Ingresa un término alemán...',
        'search_placeholder_colombia': 'Ingresa un término colombiano...',
        'search_placeholder_belgium': 'Ingresa un término belga...',
        'search_terms_title': 'Buscar términos',
        'search_terms_aria': 'Buscar términos',
        'random_terms': 'Términos aleatorios',
        'browse_all': 'Ver todos',
        'popular_categories': 'Categorías populares',
        'terms_available': 'términos disponibles',
        'close': 'Cerrar',
        
        # Country-specific translations
        'countries': 'Países',
        'home': 'Inicio',
        'explore': 'Explorar',
        'explore_argentina': 'Explorar Argentina',
        'explore_australia': 'Explorar Australia', 
        'explore_germany': 'Explorar Alemania',
        'explore_colombia': 'Explorar Colombia',
        'explore_belgium': 'Explorar Bélgica',
        'more_countries_coming_soon': 'Más Países Próximamente',
        'coming_soon': 'Próximamente',
        'choose_another_country': 'Elegir Otro País',
        'want_to_explore_another_country': '¿Querés explorar otro país?',
        'create_account': 'Crear Cuenta',
        'my_dashboard': 'Mi Panel',
        'random_terms': 'Términos Aleatorios',
        'total_terms': 'Términos Totales',
        'featured_terms': 'Términos Destacados',
        'popular_argentina': 'Popular: Lunfardo, Che, Boludo',
        'popular_australia': 'Popular: G\'day, Mate, Arvo',
        'popular_germany': 'Popular: Geil, Krass, Alter',
        'popular_colombia': 'Popular: Chimba, Parce, Bacano',
        'popular_belgium': 'Popular: Amai, Zot, Schoon',
        
        # Footer
        'made_with_love': 'Hecho con amor para el mundo',
        'github_repository': 'Repositorio GitHub',
        'about_this_project': 'Acerca de este proyecto',
        
        # Search and Interface
        'search_terms': 'Buscar términos',
        'no_results_found': 'No se encontraron resultados',
        'show_all_entries': 'Mostrar todas las entradas',
        'filter_by_category': 'Filtrar por categoría',
        'clear_filters': 'Limpiar filtros',
        
        # Authentication
        'login': 'Iniciar Sesión',
        'logout': 'Cerrar Sesión',
        'signup': 'Registrarse',
        'sign_up': 'Registrarse',
        'register': 'Registrar',
        'username': 'Usuario',
        'password': 'Contraseña',
        'confirm_password': 'Confirmar Contraseña',
        'email': 'Email',
        'first_name': 'Nombre',
        'last_name': 'Apellido',
        'welcome_back': '¡Bienvenido de vuelta!',
        'login_to_continue': 'Iniciá sesión para continuar tu viaje de aprendizaje',
        'create_account': 'Crear Cuenta',
        'join_lingoworld': '¡Unite a LingoWorld y comenzá a contribuir!',
        'already_have_account': '¿Ya tenés una cuenta?',
        'dont_have_account': '¿No tenés una cuenta?',
        'login_here': 'Iniciá sesión aquí',
        'signup_here': 'Registrate aquí',
        'login_success': '¡Bienvenido de vuelta! Has iniciado sesión exitosamente.',
        'logout_success': 'Has cerrado sesión exitosamente.',
        'signup_success': '¡Cuenta creada exitosamente! Bienvenido a LingoWorld.',
        'login_required': 'Por favor iniciá sesión para acceder a esta función.',
        'invalid_credentials': 'Usuario o contraseña inválidos.',
        'account_created': '¡Tu cuenta ha sido creada exitosamente!',
        'password_mismatch': 'Las contraseñas no coinciden.',
        'username_taken': 'Este nombre de usuario ya está en uso.',
        'email_taken': 'Este email ya está registrado.',
        'profile': 'Perfil',
        'my_contributions': 'Mis Contribuciones',
        'my_favorites': 'Mis Favoritos',
        'account_settings': 'Configuración de Cuenta',
        'contributed_by': 'Contribuido por',
        'added_by': 'Agregado por',
        'contributor': 'Colaborador',
        'add_entry': 'Agregar Término',
        'contribute': 'Contribuir',
        'edit_entry': 'Editar Término',
        'my_entries': 'Mis Términos',
        'my_profile': 'Mi Perfil',
        'entries_contributed': 'Términos Contribuidos',
        'join_community': '¡Unite a nuestra comunidad de entusiastas del idioma!',
        'added': 'Agregado',
        'updated': 'Actualizado',
        'browse_all': 'Ver todos',
        
        # Quiz System
        'slang_quiz_challenge': 'Desafío de Quiz de Jerga',
        'argentine_slang_quiz': 'Quiz de Jerga Argentina',
        'australian_slang_quiz': 'Quiz de Jerga Australiana',
        'german_slang_quiz': 'Quiz de Jerga Alemana',
        'colombian_slang_quiz': 'Quiz de Jerga Colombiana',
        'belgian_slang_quiz': 'Quiz de Jerga Belga',
        'question': 'Pregunta',
        'of': 'de',
        'score': 'Puntaje',
        'skip': 'Saltar',
        'next': 'Siguiente',
        'take_quiz': 'Hacer Quiz',
        'quiz_complete': '¡Quiz Completado!',
        'correct': '¡Correcto! +1',
        'incorrect': '¡Incorrecto!',
        'skipped': 'Saltado',
        'slang_master': '🏆 ¡Maestro de la Jerga!',
        'good_job': '⭐ ¡Buen Trabajo!',
        'keep_learning': '📚 ¡Sigue Aprendiendo!',
        'try_again': '💪 ¡Inténtalo de Nuevo!',
        'try_again_button': 'Intentar de Nuevo',
        'close_quiz': 'Cerrar',
        'loading_question': 'Cargando pregunta...',
        'percent_correct': '% Correcto',
        
        # Language Selection
        'welcome': 'BIENVENIDO',
        'choose_language': 'Elige Tu Idioma',
        'select_language_to_continue': 'Selecciona tu idioma preferido para continuar',
        'english': 'Inglés',
        'spanish': 'Español',
        'explore_global_slang_english': 'Explora jerga y expresiones globales en inglés',
        'explore_global_slang_spanish': 'Explora jerga y expresiones globales en español',
        'argentina': 'Argentina',
        'australia': 'Australia',
        'germany': 'Alemania',
        'colombia': 'Colombia',
        'belgium': 'Bélgica',
        'talk_like_local': 'Habla como un local. No como un libro de texto.',
        
        # Categories (Database Content)
        'slang': 'Jerga',
        'insults': 'Insultos',
        'tongue_twisters': 'Trabalenguas',
        'colloquial_phrases': 'Frases Coloquiales',
        'jokes': 'Chistes',
        'unique_concepts': 'Conceptos Únicos',
        
        # Parts of Speech
        'noun': 'Sustantivo',
        'verb': 'Verbo',
        'adjective': 'Adjetivo',
        'adverb': 'Adverbio',
        'interjection': 'Interjección',
        'phrase': 'Frase',
        'expression': 'Expresión',
        
        # Form Labels
        'term': 'Término',
        'language_code': 'Código de Idioma',
        'region_code': 'Código de Región',
        'part_of_speech': 'Parte de la Oración',
        'notes': 'Notas',
        'tags': 'Etiquetas',
        
        # Email Verification
        'email_verification_subject': 'Verificá tu cuenta de LingoWorld',
        'verify_email_message': 'Por favor hacé clic en el botón de abajo para verificar tu dirección de email y activar tu cuenta de LingoWorld.',
        'verify_email_button': 'Verificar Dirección de Email',
        'email_verification_pending': 'Revisá tu Email',
        'signup_success_verify_email': '¡Cuenta creada exitosamente! Por favor revisá tu email ({email}) para recibir las instrucciones de verificación.',
        'email_sending_failed': 'Error al enviar el email de verificación. Por favor intentá de nuevo.',
        'invalid_form_data': 'Por favor corregí los errores de abajo.',
        'invalid_verification_token': 'Enlace de verificación inválido. Por favor intentá de nuevo o solicitá un nuevo email de verificación.',
        'verification_token_expired': 'El enlace de verificación expiró. Por favor solicitá un nuevo email de verificación.',
        'email_already_verified': 'Tu email ya está verificado. Ahora podés iniciar sesión.',
        'email_verification_success': '¡Email verificado exitosamente! ¡Bienvenido a LingoWorld!',
        'verification_email_resent': 'Email de verificación enviado exitosamente. Por favor revisá tu bandeja de entrada.',
        'user_not_found': 'No se encontró ninguna cuenta pendiente con esa dirección de email.',
        'resend_verification': 'Reenviar Email de Verificación',
        'resend_verification_instructions': 'Ingresá tu dirección de email para recibir un nuevo enlace de verificación.',
        'verification_pending_message': 'Hemos enviado un email de verificación a tu dirección. Por favor revisá tu bandeja de entrada y hacé clic en el enlace de verificación para activar tu cuenta.',
        'didnt_receive_email': '¿No recibiste el email?',
        'resend_email': 'Reenviar Email',
        
        # Country Descriptions
        'country_descriptions': {
            'argentina': 'Explora el apasionante mundo del Lunfardo - la jerga única de Argentina',
            'australia': '¡G\'day mate! Descubre la jerga australiana auténtica desde el Outback hasta la costa',
            'germany': 'Descubre la jerga alemana desde Berlín hasta Baviera',
            'colombia': '¡Qué chimba! Experimenta la vibrante jerga colombiana desde Bogotá hasta la costa caribeña',
            'belgium': '¡Dag hé! Explora la riqueza lingüística de Bélgica - desde el ingenio flamenco hasta la calidez valona'
        },
        
        # Example Templates by Country
        'example_templates': {
            'argentina': {
                'conversation': "Escuché a un porteño decir '{}' en el café ayer...",
                'context': "El término '{}' se usa ampliamente en Buenos Aires y la región del Río de la Plata."
            },
            'australia': {
                'conversation': "Mi amigo australiano dijo '{}' cuando estábamos en la playa...",
                'context': "A menudo escucharás '{}' usado en pubs y barbacoas por toda Australia."
            },
            'germany': {
                'conversation': "En Berlín, alguien me dijo que '{}' significa...",
                'context': "La expresión '{}' es particularmente común en la cultura juvenil alemana."
            },
            'colombia': {
                'conversation': "Un amigo de Medellín me enseñó que '{}' se usa cuando...",
                'context': "En el español colombiano, '{}' refleja la vibrante cultura de la costa caribeña."
            },
            'belgium': {
                'conversation': "Mientras estaba en Bruselas, aprendí que '{}' es una expresión típica...",
                'context': "La palabra '{}' muestra la herencia multilingüe única de Bélgica."
            }
        }
    }
}

def get_translation(key, language='en', country=None, **kwargs):
    """Get translation for a key in the specified language."""
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS['en'])
    
    # Handle nested keys
    keys = key.split('.')
    value = lang_dict
    for k in keys:
        value = value.get(k, key)
        if not isinstance(value, dict):
            break
    
    # Handle country-specific translations
    if country and isinstance(value, dict):
        value = value.get(country, key)
    
    # Format with kwargs if it's a string
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value
    
    return value if value != key else key

def get_user_language(request):
    """Get user's preferred language from session."""
    return request.session.get('user_language', 'en')

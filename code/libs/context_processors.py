import settings

def app_register_context_processors(app):
    @app.context_processor
    def facebook_app_id():
        return dict(facebook_app_id=settings.API_KEY)

    @app.context_processor
    def domain_url():
        return dict(DOMAIN_URL=settings.DOMAIN_URL)

    # @app.context_processor
    # def game_timer():
    #     return dict(game_timer=settings.GAME_TIMER)
    #
    # @app.context_processor
    # def game_timer_str():
    #     return dict(game_timer=str(settings.GAME_TIMER).zfill(2))
    #
    # @app.context_processor
    # def intro_timer_str():
    #     return dict(intro_timer=str(settings.INTRO_TIMER).zfill(2))
    #
    #
    # @app.context_processor
    # def intro_timer():
    #     return dict(intro_timer=settings.INTRO_TIMER)

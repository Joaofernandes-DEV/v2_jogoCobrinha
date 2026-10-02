import pygame

from cobrinha.audio import MUSICAS_DAS_FASES, Audio, Musica, Som, musica_da_fase


def test_toca_todos_os_efeitos_e_todas_as_musicas(jogo):
    audio = jogo.audio
    assert audio.disponivel
    for som in Som:
        audio.tocar(som)
    for musica in Musica:
        audio.tocar_musica(musica)
        assert audio.musica_atual is musica
        assert pygame.mixer.music.get_busy()
    audio.pausar_musica()
    audio.retomar_musica()


def test_mesma_musica_nao_reinicia(jogo, monkeypatch):
    carregadas = []
    monkeypatch.setattr(pygame.mixer.music, "load", carregadas.append)
    monkeypatch.setattr(pygame.mixer.music, "play", lambda **kwargs: None)
    jogo.audio.tocar_musica(Musica.MENU)
    jogo.audio.tocar_musica(Musica.MENU)
    jogo.audio.tocar_musica(Musica.FASE_1)
    assert carregadas == [Musica.MENU.arquivo, Musica.FASE_1.arquivo]


def test_parar_musica_silencia_na_hora(jogo):
    jogo.audio.tocar_musica(Musica.FASE_2)
    jogo.audio.parar_musica()
    assert jogo.audio.musica_atual is None
    assert not pygame.mixer.music.get_busy()


def test_cada_fase_tem_sua_musica_e_elas_se_revezam():
    assert [musica_da_fase(n) for n in (1, 2, 3)] == list(MUSICAS_DAS_FASES)
    assert len(set(MUSICAS_DAS_FASES)) == 3
    assert Musica.MENU not in MUSICAS_DAS_FASES
    assert musica_da_fase(4) is musica_da_fase(1)


def test_mudo_zera_e_restaura_os_volumes(jogo):
    audio = jogo.audio
    audio.alternar_mudo()
    assert audio.mudo
    assert audio._sons[Som.COMER].get_volume() == 0
    assert pygame.mixer.music.get_volume() == 0
    audio.alternar_mudo()
    assert not audio.mudo
    assert audio._sons[Som.COMER].get_volume() > 0


def test_sem_saida_de_audio_o_jogo_segue_em_silencio(jogo, monkeypatch):
    def falhar(*args, **kwargs):
        raise pygame.error("sem dispositivo de áudio")

    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "init", falhar)
    audio = Audio()
    assert not audio.disponivel
    audio.tocar(Som.COMER)
    audio.tocar_musica(Musica.MENU)
    assert audio.musica_atual is Musica.MENU  # o estado segue certo mesmo sem som
    audio.parar_musica()
    audio.alternar_mudo()
    assert audio.mudo

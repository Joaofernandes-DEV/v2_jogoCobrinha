import pygame

from cobrinha.audio import Audio, Som


def test_toca_todos_os_efeitos_e_a_musica(jogo):
    audio = jogo.audio
    assert audio.disponivel
    for som in Som:
        audio.tocar(som)
    audio.tocar_musica()
    audio.pausar_musica()
    audio.retomar_musica()


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
    audio.tocar_musica()
    audio.alternar_mudo()
    assert audio.mudo

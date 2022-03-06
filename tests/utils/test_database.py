import grubberbot as gb
import alembic.config
import sqlalchemy as sa


class AlembicSetup:
    def setup_method(self, method):
        args = gb.utils.funcs.ParseArgs()
        self.db = gb.utils.Database(args, verbose=True)
        self.db.alembic_upgrade_head()
        self.db.load_schemas()

    def teardown_method(self, method):
        '''
        print('All tables:')
        for key, table in self.db.metadata.tables.items():
            print(f'* {table.schema}.{key}')
        argv = [
            #'--raiseerr',
            'downgrade',
            'base',
        ]
        alembic.config.main(argv=argv)
        '''
        pass


class TestTTS(AlembicSetup):

    def test_exists_tts(self):
        assert 'twitch.tts' in self.db.metadata.tables.keys()

    def test_exists_tts_permissions(self):
        assert 'twitch.tts_permissions' in self.db.metadata.tables.keys()

class TestRapidLeague(AlembicSetup):

    def test_exists_tts(self):
        assert 'discord.user' in self.db.metadata.tables.keys()


if __name__ == "__main__":
    pass

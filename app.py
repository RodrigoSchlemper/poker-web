
from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
import psycopg2

app = Flask(__name__)
CORS(app)

# Conexão com PostgreSQL da Railway
conn_str = "postgresql://postgres:DKKBTsDGURjkXQMdYDEFYHIhFkCHLwwl@crossover.proxy.rlwy.net:18241/railway"

def get_connection():
    return psycopg2.connect(conn_str)

@app.route("/ranking")
def get_ranking():
    query = """
    SELECT
      PosicaoGeral AS posicaoageral,
      Nome AS nome,
      PontuacaoTotal AS pontuacaototal,
      PrimeiroLugar AS primeirolugar,
      SegundoLugar AS segundolugar,
      TerceiroLugar AS terceirolugar,
      QuartoLugar AS quartolugar,
      QuintoLugar AS quintolugar,
      SextoLugar AS sextolugar,
      SetimoLugar AS setimolugar,
      OitavoLugar AS oitavolugar,
      NonoLugar AS nonolugar,
      DecimoLugar AS decimolugar,
      UltimoLugar AS ultimolugar
    FROM RankingGeral
    ORDER BY PosicaoGeral
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/ranking_anual/<int:ano>")
def get_ranking_anual(ano):
    query = f"""
        SELECT *
        FROM RankingAnual
        WHERE Ano = {ano}
        ORDER BY PosicaoAnual, PrimeiroLugar DESC, SegundoLugar DESC,
                 TerceiroLugar DESC, QuartoLugar DESC, QuintoLugar DESC
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/jogos")
def get_jogos():
    query = """
    SELECT data_do_jogo, 
    "Golum", "Edson", "Duda", "João", "Jorge",
    "Miguel", "Guilherme", "Jonata", "Biel", "Brunão",
    "Carlos", "Vitor", "Luan", "Joao Fillipe", "Bruno",
    "Hang", "Murilo", "Piracema", "Anderson", "Vinicius"
    FROM vw_posicoes_pivotadas
    ORDER BY data_do_jogo DESC
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/posicoes")
def get_posicoes():
    query = "SELECT * FROM vw_posicoes_pivotadas ORDER BY data_do_jogo"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    colnames = [desc[0] for desc in cur.description]
    data = [dict(zip(colnames, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route("/test")
def test_conn():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([t[0] for t in tables])

@app.route("/cadastrar_jogo", methods=["POST"])
def cadastrar_jogo():
    data = request.json.get("data")
    posicoes = request.json.get("posicoes", {})

    if not data or not posicoes:
        return jsonify({"message": "Dados incompletos"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Inserir o jogo
        cur.execute("INSERT INTO Jogo (Data) VALUES (%s) RETURNING Id", (data,))
        jogo_id = cur.fetchone()[0]

        # Inserir participações
        for nome, posicao in posicoes.items():
            cur.execute("SELECT Id FROM Jogador WHERE Nome = %s", (nome,))
            jogador = cur.fetchone()
            if jogador:
                jogador_id = jogador[0]
                cur.execute(
                    "INSERT INTO Participacao (IdJogo, IdJogador, Posicao) VALUES (%s, %s, %s)",
                    (jogo_id, jogador_id, posicao)
                )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Jogo cadastrado com sucesso!"})

    except Exception as e:
        print("Erro:", e)
        return jsonify({"message": "Erro ao cadastrar jogo"}), 500


if __name__ == "__main__":
    app.run(debug=True)

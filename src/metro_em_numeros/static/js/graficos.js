
(function () {
  "use strict";

  var seletor = document.getElementById("serie");
  var aviso = document.getElementById("aviso-grafico");
  var tela = document.getElementById("grafico");
  var grafico = null;

  function groupsofdata(dados) {
    return dados.series.map(function (serie) {
      var total = serie.nome.indexOf("Total") === 0;
      return {
        label: serie.nome,
        data: serie.valores,   // null = sem dados: a linha fica interrompida
        spanGaps: false,
        borderWidth: total ? 3 : 1.5,
        tension: 0.2
      };
    });
  }

  function draw(dados) {
    if (grafico) { grafico.destroy(); }
    grafico = new Chart(tela, {
      type: "line",
      data: { labels: dados.anos, datasets: groupsofdata(dados) },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: dados.titulo + " (" + dados.unidade + ")" }
        },
        scales: { y: { title: { display: true, text: dados.unidade } } }
      }
    });
  }

  function load(chave) {
    aviso.textContent = "A carregar…";
    fetch("/api/series/" + encodeURIComponent(chave))
      .then(function (resposta) {
        if (!resposta.ok) { throw new Error("erro " + resposta.status); }
        return resposta.json();
      })
      .then(function (dados) {
        aviso.textContent = dados.nota || "";
        draw(dados);
      })
      .catch(function (erro) {
        aviso.textContent = "Não foi possível carregar o gráfico: " + erro.message;
      });
  }

  if (typeof Chart === "undefined") {
    aviso.textContent =
      "Falta o ficheiro static/js/chart.umd.min.js (ver instruções no README).";
    return;
  }
  seletor.addEventListener("change", function () { load(seletor.value); });
  if (seletor.value) { load(seletor.value); }
})();
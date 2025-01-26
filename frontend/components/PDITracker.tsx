import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Progress } from '@/components/ui/progress';
import { Calendar, CheckCircle, Circle, ExternalLink, Clock } from 'lucide-react';
import '../styles/pdi-tracker.css';

// Tipos TypeScript que espelham os modelos Pydantic
interface AtividadeEducacional {
  id: string;
  titulo: string;
  descricao: string;
  trimestre: number;
  tipo: 'curso' | 'mentoria' | 'projeto' | 'workshop' | 'leitura' | 'outro';
  link?: string;
  plataforma?: string;
  dataInicio?: string;
  dataFim?: string;
  tags?: string[];
}

interface PDIConfig {
  titulo: string;
  subtitulo?: string;
  colaborador: string;
  periodo: string;
  atividades: AtividadeEducacional[];
}

interface PDITrackerProps {
  config: PDIConfig;
  onProgressUpdate?: (progress: number) => void;
  onAtividadeConcluida?: (atividadeId: string, concluida: boolean) => void;
}

const PDITracker: React.FC<PDITrackerProps> = ({ 
  config, 
  onProgressUpdate,
  onAtividadeConcluida 
}) => {
  const [atividadesConcluidas, setAtividadesConcluidas] = useState<Set<string>>(new Set());

  const calcularProgresso = (concluidas: Set<string>): number => {
    return (concluidas.size / config.atividades.length) * 100;
  };

  const handleToggleConclusao = (atividadeId: string) => {
    setAtividadesConcluidas(prev => {
      const novoSet = new Set(prev);
      if (novoSet.has(atividadeId)) {
        novoSet.delete(atividadeId);
      } else {
        novoSet.add(atividadeId);
      }
      return novoSet;
    });
  };

  useEffect(() => {
    const progresso = calcularProgresso(atividadesConcluidas);
    onProgressUpdate?.(progresso);

  }, [atividadesConcluidas, config.atividades.length]);

  return (
    <div className="pdi-tracker">
      <header className="pdi-header">
        <h1>{config.titulo}</h1>
        {config.subtitulo && <h2>{config.subtitulo}</h2>}

        <div className="pdi-info">
          <span><Calendar className="icon" /> {config.periodo}</span>
          <span><Clock className="icon" /> {config.colaborador}</span>
        </div>

        <Progress value={calcularProgresso(atividadesConcluidas)} />
      </header>

      <div className="atividades-grid">
        {[1, 2, 3, 4].map(trimestre => (
          <div key={trimestre} className="trimestre-section">
            <h3>{trimestre}º Trimestre</h3>
            <div className="atividades-list">
              {config.atividades
                .filter(ativ => ativ.trimestre === trimestre)
                .map(atividade => (
                  <div
                    key={atividade.id}
                    className={`atividade-card ${atividadesConcluidas.has(atividade.id) ? 'concluida' : ''}`}
                  >
                    <div className="atividade-header">
                      <h4>{atividade.titulo}</h4>
                      <button
                        onClick={() => handleToggleConclusao(atividade.id)}
                        className="conclusao-btn"
                      >
                        {atividadesConcluidas.has(atividade.id) ? (
                          <CheckCircle className="icon checked" />
                        ) : (
                          <Circle className="icon" />
                        )}
                      </button>
                    </div>
                    <p>{atividade.descricao}</p>
                    <div className="atividade-meta">
                      <span className="tipo">{atividade.tipo}</span>
                      {atividade.link && atividade.plataforma && atividade.link.length > 0 && atividade.plataforma.length > 0 && (
                        <a
                          href={atividade.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="link-btn"
                        >
                          <ExternalLink className="icon" />
                          {atividade.plataforma}
                        </a>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Função de renderização para Streamlit
const renderPDITracker = (
  container: HTMLElement,
  config: PDIConfig,
  height: number = 600
) => {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <PDITracker
        config={config}
        onProgressUpdate={(progress) => {
          // Notificar Streamlit sobre o progresso
          if (window.Streamlit) {
            window.Streamlit.setComponentValue({ progress });
          }
        }}
      />
    </React.StrictMode>
  );
};

// Declaração de tipos para o window global
declare global {
  interface Window {
    renderPDITracker: typeof renderPDITracker;
    Streamlit: any;
  }
}

// Expor a função de renderização globalmente
window.renderPDITracker = renderPDITracker;

export default PDITracker;
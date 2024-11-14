import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import './ProjectInput.css';

const ProjectInput = () => {
  const [input, setInput] = useState('');
  const [diagram, setDiagram] = useState(null);
  const [steps, setSteps] = useState('');
  const [isGenerated, setIsGenerated] = useState(false);

  const handleSubmit = async () => {
    try {
      const response = await axios.post('http://localhost:8000/generate-diagram-and-steps', { input });
      setDiagram(response.data.diagram);
      setSteps(response.data.steps);
      setIsGenerated(true);
    } catch (error) {
      console.error('Error generating diagram and steps:', error);
    }
  };

  return (
    <div className="main-container">
      <div className="background-overlay"></div>
      <AnimatePresence>
        {!isGenerated && (
          <motion.div
            className="glass-card input-card"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -300 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="title">ArcNova</h1>
            <textarea
              className="input-box"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your project idea..."
            />
            <motion.button
              className="generate-button"
              onClick={handleSubmit}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Generate Diagram and Steps
            </motion.button>
          </motion.div>
        )}

        {isGenerated && (
          <motion.div
            className="results-container"
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8 }}
          >
            <div className="diagram-box">
              <h2 className="subtitle">Architecture Diagram</h2>
              <div className="diagram-container">
                <img
                  src={`data:image/png;base64,${diagram}`}
                  alt="AWS Architecture Diagram"
                  className="diagram"
                />
              </div>
            </div>
            <div className="steps-box">
              <h2 className="subtitle">Implementation Steps</h2>
              <ReactMarkdown className="steps">{steps}</ReactMarkdown>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProjectInput;

/**
 * Data-analysis skills catalog plugin for OpenCode.ai
 *
 * Registers the skills directory so OpenCode discovers all skills
 * without symlinks or manual config.
 */

import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const DataAnalysisPlugin = async () => {
  const skillsDir = path.resolve(__dirname, "../../skills");

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },
  };
};

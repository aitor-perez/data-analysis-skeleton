/**
 * Data-analysis skills catalog plugin for OpenCode.ai
 *
 * Registers the skills directory so OpenCode discovers all
 * data-analysis-* skills without symlinks or manual config.
 *
 * Skills are invoked explicitly by the user (e.g. via the native skill tool).
 * This plugin does not inject any automatic bootstrap context.
 */

import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const DataAnalysisPlugin = async () => {
  const skillsDir = path.resolve(__dirname, "../..");

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

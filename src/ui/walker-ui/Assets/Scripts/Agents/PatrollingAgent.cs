using System;

using UnityEngine;

namespace Agents {
    [Serializable]
    public class PatrollingAgentConfig : BaseAgentConfig {
    }

    public class PatrollingAgent : BaseAgent<PatrollingAgentConfig> {
        public PatrollingAgent(PatrollingAgentConfig config, Walker walker) : base(config, walker) { }

        protected override Vector3 Velocity => Vector3.zero;

        public override void Init() { }

        public override void Step() { }
    }
}

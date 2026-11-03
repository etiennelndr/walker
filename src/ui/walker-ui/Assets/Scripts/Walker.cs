using Agents;

using UnityEngine;

public enum WalkerBehaviour {
    Patrolling,
    Training
}

public class Walker : MonoBehaviour {
    [SerializeField]
    [Tooltip("Behaviour of the walker, which also selects the settings shown below")]
    private WalkerBehaviour behaviour;

    [SerializeField]
    [Tooltip("Settings of the Training behaviour")]
    private TrainingAgentConfig trainingAgentConfig;

    [SerializeField]
    [Tooltip("Settings of the Patrolling behaviour")]
    private PatrollingAgentConfig patrollingAgentConfig;

    private BaseAgent _agent;

    // Start is called before the first frame update
    private void Start() {
        switch (behaviour) {
            case WalkerBehaviour.Patrolling: {
                _agent = new PatrollingAgent(patrollingAgentConfig, this);
                break;
            }
            case WalkerBehaviour.Training: {
                _agent = new TrainingAgent(trainingAgentConfig, this);
                break;
            }
            default: {
                Debug.LogError($"Unhandled behaviour: {behaviour}", this);
                enabled = false;
                return;
            }
        }

        _agent.Init();
    }

    // Update is called once per frame
    private void Update() {
        _agent.Step();
    }
}

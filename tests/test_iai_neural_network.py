import unittest

from Lando_Project.infra.iai_neural_network import (
    IAIDecisionEngine,
    InstinctCircuit,
    IntuitiveLearningLayer,
    TelemetryInput,
)


class TestIAINeuralNetwork(unittest.TestCase):
    def test_reflex_path_uses_ips_when_confident(self):
        engine = IAIDecisionEngine(threshold=0.5)
        telemetry = TelemetryInput(
            battery_level=0.9,
            cpu_demand=0.4,
            cpu_temp_c=50,
            network_mbps=20,
            disk_iops=200,
            latency_ms=40,
        )
        signature = engine.ill.encode(telemetry).features
        engine.ips.circuits = [
            InstinctCircuit(
                name="test_reflex",
                signature=signature,
                action="maintain_policy_with_predictive_monitoring",
            )
        ]

        result = engine.decide(telemetry, energy_budget=0.4)

        self.assertEqual(result.source_layer, "IPS")
        self.assertGreaterEqual(result.confidence, 0.99)
        self.assertEqual(len(result.topology), 10)
        self.assertEqual(result.topology[0], 1)
        self.assertEqual(result.topology[-1], 1)

    def test_cognition_path_learns_new_circuit(self):
        engine = IAIDecisionEngine(threshold=0.95)
        initial_circuits = len(engine.ips.circuits)

        telemetry = TelemetryInput(
            battery_level=0.1,
            cpu_demand=0.95,
            cpu_temp_c=92,
            network_mbps=800,
            disk_iops=9000,
            latency_ms=350,
        )

        result = engine.decide(telemetry, energy_budget=0.9)

        self.assertEqual(result.source_layer, "CLL")
        self.assertGreater(result.confidence, 0.8)
        self.assertGreater(len(engine.ips.circuits), initial_circuits)

    def test_internal_contradiction_uses_low_battery_signal(self):
        ill = IntuitiveLearningLayer()

        low_battery = TelemetryInput(
            battery_level=0.1,
            cpu_demand=0.9,
            cpu_temp_c=40,
            network_mbps=10,
            disk_iops=100,
            latency_ms=10,
        )
        high_battery = TelemetryInput(
            battery_level=0.9,
            cpu_demand=0.9,
            cpu_temp_c=40,
            network_mbps=10,
            disk_iops=100,
            latency_ms=10,
        )

        low_internal = ill.encode(low_battery).features[0]
        high_internal = ill.encode(high_battery).features[0]

        self.assertGreater(low_internal, high_internal)
        self.assertEqual(high_internal, 0.0)



if __name__ == "__main__":
    unittest.main()

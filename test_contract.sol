pragma solidity ^0.4.16;

contract TestVulnerabilities {
    mapping (address => uint) private userBalances;

    // A function with a reentrancy vulnerability
    function withdraw(uint amount) public {
        if (userBalances[msg.sender] >= amount) {
            // This line is similar to many reentrancy vulnerabilities
            require(msg.sender.call.value(amount)());
            userBalances[msg.sender] -= amount;
        }
    }

    // A function with a time manipulation vulnerability
    function getReward() public {
        if (block.timestamp > 1546300800) { // Timestamp dependency
            // give reward
        }
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script, console} from "forge-std/Script.sol";
import {RareProtocolMock} from "../src/RareProtocolMock.sol";

contract DeployMock is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");

        vm.startBroadcast(deployerKey);

        RareProtocolMock mock = new RareProtocolMock();

        vm.stopBroadcast();

        console.log("RareProtocolMock deployed at:");
        console.logAddress(address(mock));
    }
}
